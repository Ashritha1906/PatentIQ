import React, { useState, useEffect } from 'react';

const PALETTES = {
  indigo: { primary: '#6366f1', light: '#818cf8', glow: 'rgba(99, 102, 241, 0.08)' },
  blue: { primary: '#2563eb', light: '#60a5fa', glow: 'rgba(37, 99, 235, 0.08)' },
  teal: { primary: '#0d9488', light: '#2dd4bf', glow: 'rgba(13, 148, 136, 0.08)' }
};

export default function SettingsPage({ userSettings, onUpdateSettings }) {
  const [apiKey, setApiKey] = useState(userSettings?.apiKey || '');
  const [mockLLM, setMockLLM] = useState(userSettings?.mockLLM !== false);
  const [activePalette, setActivePalette] = useState(userSettings?.palette || 'indigo');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (userSettings) {
      setApiKey(userSettings.apiKey || '');
      setMockLLM(userSettings.mockLLM !== false);
      setActivePalette(userSettings.palette || 'indigo');
    }
  }, [userSettings]);

  const handleApplyPalette = (paletteName) => {
    const p = PALETTES[paletteName];
    if (p) {
      document.documentElement.style.setProperty('--primary', p.primary);
      document.documentElement.style.setProperty('--primary-light', p.light);
      document.documentElement.style.setProperty('--primary-glow', p.glow);
      setActivePalette(paletteName);
    }
  };

  const handleSave = (e) => {
    e.preventDefault();
    handleApplyPalette(activePalette);
    onUpdateSettings({
      apiKey,
      mockLLM,
      palette: activePalette
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="container" style={{ maxWidth: '800px', margin: '40px auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
          Configuration
        </span>
        <h1 style={{ fontSize: '26px', fontWeight: 700, color: '#fff' }}>System Settings</h1>
      </div>

      <div className="panel panel-padding" style={{ background: 'var(--bg-surface)' }}>
        <form onSubmit={handleSave}>
          {/* Accent Color Section */}
          <div style={{ marginBottom: '28px' }}>
            <label className="input-label">Theme Accent Color</label>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              Select a custom color system token to personalize the dashboard and controls:
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              {Object.keys(PALETTES).map((name) => (
                <button
                  key={name}
                  type="button"
                  onClick={() => handleApplyPalette(name)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 16px',
                    borderRadius: 'var(--border-radius-md)',
                    border: activePalette === name ? '2px solid var(--primary)' : '1px solid var(--border-neutral)',
                    background: 'var(--bg-surface-secondary)',
                    color: '#fff',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: 500,
                    textTransform: 'capitalize'
                  }}
                >
                  <span style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: PALETTES[name].primary
                  }}></span>
                  {name}
                </button>
              ))}
            </div>
          </div>

          {/* Mock LLM Mode */}
          <div style={{ marginBottom: '28px' }}>
            <label className="input-label">Gemini RAG Mode</label>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              Toggle between live Gemini API invocations and simulated local RAG models to stay within free-tier quotas:
            </p>
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontSize: '14px', color: '#fff' }}>
              <input
                type="checkbox"
                checked={mockLLM}
                onChange={(e) => setMockLLM(e.target.checked)}
                style={{ width: '16px', height: '16px', accentColor: 'var(--primary)' }}
              />
              Enable Mock LLM Simulation (Recommended for quota savings)
            </label>
          </div>

          {/* API Key */}
          <div style={{ marginBottom: '28px' }}>
            <label className="input-label" htmlFor="apiKeyInput">Gemini API Key</label>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              Override the `.env` API Key with a custom Google Generative AI key for live analyses:
            </p>
            <input
              id="apiKeyInput"
              type="password"
              className="text-field"
              placeholder="AIzaSy..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              disabled={mockLLM}
              style={{ opacity: mockLLM ? 0.5 : 1 }}
            />
          </div>

          {/* Submit Button */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '16px', borderTop: '1px solid var(--border-neutral)', paddingTop: '20px' }}>
            {saved && (
              <span style={{ color: 'var(--success)', fontSize: '13px', fontWeight: 500 }}>
                ✓ Settings saved successfully
              </span>
            )}
            <button type="submit" className="btn-primary">
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
