import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('docs/evaluation/phase6a1_query_validation_report.json', encoding='utf-8'))
for q in d:
    print('='*75)
    print(f"QUERY {q['id']}: {q['title']}")
    print(f"Latency: {q['latency_ms']} ms | Novelty: {q['novelty_score']}/100 ({q['novelty_band']})")
    print("Top 5 Patents:")
    for p in q['top_5_patents']:
        print(f"  #{p['rank']} [{p['publication_number']}] {p['title'][:60]}... | Hybrid: {p['hybrid_score']:.4f} | Semantic: {p['semantic_score']:.4f}")
    print("Concept Coverages:")
    for c in q['concept_coverages']:
        eq_str = f" -> Eq: {', '.join(c.get('equivalents', []))}" if c.get('equivalents') else ""
        print(f"  - {c['concept']:<34}: {c['coverage_score']:>3}% [{c['coverage_band']}]{eq_str}")
    print(f"Whitespaces ({len(q['whitespaces'])}):")
    for w in q['whitespaces']:
        combo_tag = "[COMBO]" if w.get('is_combination') else "[CONCEPT]"
        print(f"  * {combo_tag} {w['concept']}: {w['coverage_score']}% ({w['representation_status']})")
