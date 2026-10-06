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
    } catch (_) {
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
    } catch (_) {
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
    } catch (_) {}
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
