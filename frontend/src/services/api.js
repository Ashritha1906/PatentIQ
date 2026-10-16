/**
 * PatentIQ API Client Service
 */

const API_BASE = '/api';

export async function checkSystemHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Health check returned status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Client: health check failed', error);
    return { status: 'unhealthy', database: 'disconnected', error: error.message };
  }
}

export async function searchNaturalLanguage({ query, topK = 10, includeRag = false, domainFilter = null, applicantFilter = null }) {
  const payload = {
    query,
    top_k: topK,
    include_rag: includeRag,
    domain_filter: domainFilter || null,
    applicant_filter: applicantFilter || null
  };
  
  const response = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
    let errMsg = `Server returned status: ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson && errorJson.detail) {
        errMsg = errorJson.detail;
      }
    } catch {
      // Ignore JSON parse errors on non-JSON response
    }
    throw new Error(errMsg);
  }
  
  return await response.json();
}

export async function analyzeIdea({ ideaText, topK = 5, domainFilter = null, applicantFilter = null }) {
  const payload = {
    idea_text: ideaText,
    top_k: topK,
    domain_filter: domainFilter || null,
    applicant_filter: applicantFilter || null
  };
  
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
    let errMsg = `Server returned status: ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson && errorJson.detail) {
        errMsg = errorJson.detail;
      }
    } catch {
      // Ignore JSON parse errors on non-JSON response
    }
    throw new Error(errMsg);
  }
  
  return await response.json();
}

export async function chatCopilot({ message, sessionId = null, sourceMode = 'hybrid', topK = 5 }) {
  const payload = {
    message,
    session_id: sessionId || null,
    source_mode: sourceMode || 'hybrid',
    top_k: topK || 5
  };

  const response = await fetch(`${API_BASE}/copilot/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errMsg = `Server returned status: ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson && errorJson.detail) {
        errMsg = errorJson.detail;
      }
    } catch {}
    throw new Error(errMsg);
  }

  return await response.json();
}

export async function getCopilotSession(sessionId) {
  const response = await fetch(`${API_BASE}/copilot/session/${sessionId}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  });
  if (!response.ok) return null;
  return await response.json();
}

export async function deleteCopilotSession(sessionId) {
  const response = await fetch(`${API_BASE}/copilot/session/${sessionId}`, {
    method: 'DELETE',
    headers: { 'Accept': 'application/json' }
  });
  return response.ok;
}


export async function comparePatents({ patents = null, patentIds = null, sessionId = null }) {
  const payload = {
    patents: patents || null,
    patent_ids: patentIds || null,
    session_id: sessionId || null,
  };

  const response = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errMsg = `Comparison request failed with status: ${response.status}`;
    try {
      const err = await response.json();
      if (err && err.detail) errMsg = err.detail;
    } catch {}
    throw new Error(errMsg);
  }

  return await response.json();
}

export async function getPatentDeepDive({ patent = null, patentId = null, comparisonContext = null }) {
  const payload = {
    patent: patent || null,
    patent_id: patentId || null,
    comparison_context: comparisonContext || null,
  };

  const response = await fetch(`${API_BASE}/compare/deep-dive`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errMsg = `Deep dive request failed with status: ${response.status}`;
    try {
      const err = await response.json();
      if (err && err.detail) errMsg = err.detail;
    } catch {}
    throw new Error(errMsg);
  }

  return await response.json();
}

export async function analyzeInnovation({ idea, sourceMode = 'hybrid', topK = 10, comparisonContext = null }) {
  const payload = {
    idea,
    source_mode: sourceMode || 'hybrid',
    top_k: topK || 10,
    comparison_context: comparisonContext || null,
  };

  const response = await fetch(`${API_BASE}/innovation/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errMsg = `Innovation analysis failed with status: ${response.status}`;
    try {
      const err = await response.json();
      if (err && err.detail) errMsg = err.detail;
    } catch {}
    throw new Error(errMsg);
  }

  return await response.json();
}

export async function generateReport({
  title = null,
  inventionDescription = null,
  query = null,
  sourceMode = 'hybrid',
  topK = 10,
  sessionId = null,
  selectedPatentIds = null,
  includeComparison = true,
  includeInnovation = true,
  comparisonPatents = null,
  comparisonResults = null,
  innovationResults = null,
  searchResults = null
}) {
  const payload = {
    title,
    invention_description: inventionDescription,
    query,
    source_mode: sourceMode,
    top_k: topK,
    session_id: sessionId,
    selected_patent_ids: selectedPatentIds,
    include_comparison: includeComparison,
    include_innovation: includeInnovation,
    comparison_patents: comparisonPatents,
    comparison_results: comparisonResults,
    innovation_results: innovationResults,
    search_results: searchResults
  };

  const response = await fetch(`${API_BASE}/reports/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errMsg = `Report generation failed with status: ${response.status}`;
    try {
      const err = await response.json();
      if (err && err.detail) errMsg = err.detail;
    } catch {}
    throw new Error(errMsg);
  }

  return await response.json();
}

export async function getReport(reportId) {
  const response = await fetch(`${API_BASE}/reports/${encodeURIComponent(reportId)}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to retrieve report ${reportId}`);
  }

  return await response.json();
}

export function getReportMarkdownUrl(reportId) {
  return `${API_BASE}/reports/${encodeURIComponent(reportId)}/markdown`;
}

export function getReportPdfUrl(reportId) {
  return `${API_BASE}/reports/${encodeURIComponent(reportId)}/pdf`;
}

