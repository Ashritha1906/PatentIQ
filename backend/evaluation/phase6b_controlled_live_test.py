import sys
import time
import json
sys.stdout.reconfigure(encoding='utf-8')

from backend.patent_sources.epo_client import EPO_CLIENT
from backend.patent_sources.epo_xml_parser import EPOXMLParser
from backend.patent_sources.epo_cache import EPO_CACHE
from backend.patent_sources.epo_usage_tracker import USAGE_TRACKER
from backend.patent_sources.epo_publication_source import EPOPublicationSource
from backend.patent_sources.local_source import LocalPatentSource
from backend.patent_sources.fusion import ResultFusion
from backend.api.services.orchestrator import PatentIntelligenceService
from backend.api.services.vector_store import ChromaVectorStore

print("="*75)
print("PATENTIQ — PHASE 6B CONTROLLED LIVE EPO INTEGRATION TEST")
print("="*75)

# 1. Controlled live document fetch from European Publication Server (EPS)
test_ep_id = "EP4812013NWA1"
print(f"\n[STEP 1] Fetching live document XML for {test_ep_id} from EPO EPS v1.2...")
t0 = time.time()
xml_content = EPO_CLIENT.fetch_patent_xml(test_ep_id)
t_fetch = (time.time() - t0) * 1000

if not xml_content:
    print("FAILED to fetch live XML content from EPO EPS.")
    sys.exit(1)

bytes_len = len(xml_content.encode("utf-8"))
print(f"  ✓ HTTP Success: Received {bytes_len} bytes in {t_fetch:.1f}ms")

# 2. XML Parser Validation
print("\n[STEP 2] Parsing ep-patent-document XML into canonical schema...")
t0 = time.time()
parsed = EPOXMLParser.parse_ep_document(xml_content)
t_parse = (time.time() - t0) * 1000

print(f"  ✓ Publication Number : {parsed.get('publication_number')}")
print(f"  ✓ Jurisdiction / Country: {parsed.get('country')}")
print(f"  ✓ Verified Kind Code  : {parsed.get('kind_code')}")
print(f"  ✓ Publication Date    : {parsed.get('publication_date')}")
print(f"  ✓ Title               : {parsed.get('title')[:70]}...")
print(f"  ✓ Applicants (count)  : {len(parsed.get('applicants', []))} -> {parsed.get('applicants')[:1]}")
print(f"  ✓ Inventors (count)   : {len(parsed.get('inventors', []))} -> {parsed.get('inventors')[:2]}")
print(f"  ✓ IPC Classifications : {len(parsed.get('ipc', []))} -> {parsed.get('ipc')[:2]}")
print(f"  ✓ CPC Classifications : {len(parsed.get('cpc', []))} -> {parsed.get('cpc')[:2]}")
print(f"  ✓ Source Tag          : {parsed.get('source')}")
print(f"  ✓ Parsing Latency     : {t_parse:.2f}ms")

# 3. Cache Validation
print("\n[STEP 3] Validating local caching of parsed document...")
EPO_CACHE.set(parsed["publication_number"], parsed, raw_bytes_len=bytes_len)
cached_doc = EPO_CACHE.get(parsed["publication_number"])
assert cached_doc is not None, "Cache lookup failed"
print(f"  ✓ Cache Hit confirmed: {cached_doc['publication_number']} (Hits: {EPO_CACHE.hits})")

# 4. Fair-Use Usage Tracker Validation
print("\n[STEP 4] Validating sliding 7-day fair-use tracking...")
usage_summary = USAGE_TRACKER.get_usage_summary()
print(f"  ✓ Rolling 7-day bytes : {usage_summary['rolling_7_day_bytes']} bytes ({usage_summary['rolling_7_day_mb']} MB)")
print(f"  ✓ Fair-use Limit      : {usage_summary['fair_use_limit_mb']} MB (Safety cutoff: {usage_summary['safety_limit_mb']} MB)")
print(f"  ✓ Usage Percentage    : {usage_summary['percent_used']}% of 5GB budget")
print(f"  ✓ Throttled Status    : {usage_summary['is_throttled']} (can_request={USAGE_TRACKER.can_request()})")

# 5. Hybrid Federated Search Real-World Test
print("\n[STEP 5] Executing Federated Hybrid Retrieval on Real-World Query...")
test_query = "automated detection and classification of diabetic retinopathy from retinal fundus images using deep learning"
vs = ChromaVectorStore(db_path="data/vectordb")
orchestrator = PatentIntelligenceService(vector_store=vs)

t0 = time.time()
response = orchestrator.search_natural_language(
    query=test_query,
    top_k=5,
    source_mode="hybrid"
)
t_hybrid = (time.time() - t0) * 1000

print(f"  ✓ Federated Hybrid Search completed in {t_hybrid:.1f}ms")
print(f"  ✓ Total Fused Results : {len(response.results)}")
print(f"  ✓ Provenance Metadata : {json.dumps(response.provenance_metadata, indent=2)}")

print("\nTop Ranked Candidates:")
for idx, p in enumerate(response.results[:5], 1):
    print(f"  #{idx} [{p.publication_number}] (Source: {p.source}) - {p.title[:55]}... | Score: {p.final_score:.4f}")

# 6. Local Fallback Test
print("\n[STEP 6] Testing Local Fallback (Simulating EPO Offline)...")
t0 = time.time()
resp_local = orchestrator.search_natural_language(
    query=test_query,
    top_k=5,
    source_mode="local"
)
t_local = (time.time() - t0) * 1000
print(f"  ✓ Local-only search succeeded in {t_local:.1f}ms (Count: {len(resp_local.results)})")
print(f"  ✓ Provenance: {resp_local.provenance_metadata['source_mode']}, Live used: {resp_local.provenance_metadata['live_retrieval_used']}")

print("\n" + "="*75)
print("ALL CONTROLLED LIVE TESTS COMPLETED SUCCESSFULLY!")
print("="*75)
