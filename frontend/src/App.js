import React, { useState, useEffect, useCallback } from 'react';
import pdfMake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';
import { projectsApi } from './api/projects';
import { entriesApi } from './api/entries';
import { templatesApi } from './api/templates';
import { processTemplate, formatDateDE, calculatePaymentDeadline } from './utils/templateProcessor';
import './App.css';

// Initialize pdfMake fonts
pdfMake.vfs = pdfFonts.vfs;

const BUILTIN_TEMPLATE_ID = 'anschreiben_gewerk';

/** Evaluate a JSON-serialized condition: { field, equals } */
function evalCondition(condition, formData) {
  if (!condition) return true;
  return formData[condition.field] === condition.equals;
}

/** Build initial form data from a field_config array */
function buildInitialFormData(fields) {
  const data = {};
  if (!fields) return data;
  fields.forEach(field => {
    if (field.defaultValue === 'today') {
      data[field.code] = new Date().toISOString().split('T')[0];
    } else if (field.defaultValue) {
      data[field.code] = field.defaultValue;
    } else {
      data[field.code] = '';
    }
  });
  return data;
}

function App() {
  // ── API / remote state ─────────────────────────────────────────────────────
  const [projects, setProjects]               = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [entries, setEntries]                 = useState([]);
  const [templates, setTemplates]             = useState([]);
  const [apiConnected, setApiConnected]       = useState(false);
  const [apiError, setApiError]               = useState(null);

  // ── Template / form state ──────────────────────────────────────────────────
  const [activeTemplateId, setActiveTemplateId]     = useState(BUILTIN_TEMPLATE_ID);
  const [activeTemplate, setActiveTemplate]         = useState(null);  // full template object
  const [activeFieldConfig, setActiveFieldConfig]   = useState([]);
  const [formData, setFormData]                     = useState({});
  const [pdfUrl, setPdfUrl]                         = useState(null);

  // ── Entry tracking ─────────────────────────────────────────────────────────
  const [currentEntryId, setCurrentEntryId]     = useState(null);
  const [currentEntryName, setCurrentEntryName] = useState('');
  const [saveEntryName, setSaveEntryName]       = useState('');

  // ── Project creation ───────────────────────────────────────────────────────
  const [newProjectName, setNewProjectName] = useState('');

  // ── Auto-save state ────────────────────────────────────────────────────────
  const [autoSavingProjects, setAutoSavingProjects] = useState(new Set());

  // ── Sidebar resizing ────────────────────────────────────────────────────────
  const [sidebarWidth, setSidebarWidth] = useState(240);
  const [isResizing, setIsResizing] = useState(false);

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e) => {
      const newWidth = Math.max(150, Math.min(e.clientX, 600)); // Min 150px, max 600px
      setSidebarWidth(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  // ── Load projects + templates on mount ────────────────────────────────────
  useEffect(() => {
    async function init() {
      try {
        const [projs, tpls] = await Promise.all([
          projectsApi.list(),
          templatesApi.list(),
        ]);
        setProjects(projs);
        setTemplates(tpls);
        
        // If there are templates, load the first one; otherwise wait for user to upload
        if (tpls.length > 0) {
          const firstTpl = tpls[0];
          setActiveTemplateId(firstTpl.id);
          setActiveTemplate(firstTpl);
          setActiveFieldConfig(firstTpl.field_config || []);
          setFormData(buildInitialFormData(firstTpl.field_config));
        } else {
          // No templates yet - show empty state
          setActiveTemplate(null);
          setActiveFieldConfig([]);
          setFormData({});
        }
        
        setApiConnected(true);
      } catch (e) {
        setApiError('Backend nicht erreichbar. Bitte Backend starten: cd backend && .venv/bin/uvicorn main:app --reload');
      }
    }
    init();
  }, []);

  // ── Load entries when selected project changes ─────────────────────────────
  useEffect(() => {
    if (!selectedProject) { 
      setEntries([]); 
      return; 
    }
    
    // Load entries for this project
    entriesApi.list(selectedProject.id)
      .then(setEntries)
      .catch(() => setEntries([]));
    
    // Load project's saved form data if it exists
    if (selectedProject.form_data) {
      setFormData(selectedProject.form_data);
    } else {
      // Initialize with current template's fields
      setFormData(buildInitialFormData(activeFieldConfig));
    }
    setPdfUrl(null);
  }, [selectedProject, activeFieldConfig]);

  // ── Auto-save project when formData changes ────────────────────────────────
  const saveProjectToBackend = useCallback(async () => {
    if (!selectedProject) return;
    
    try {
      setAutoSavingProjects(prev => new Set([...prev, selectedProject.id]));
      const updated = await projectsApi.update(selectedProject.id, {
        form_data: formData,
      });
      setProjects(prev => prev.map(p => p.id === updated.id ? updated : p));
      setSelectedProject(updated);
      setAutoSavingProjects(prev => {
        const next = new Set(prev);
        next.delete(selectedProject.id);
        return next;
      });
    } catch (e) {
      console.error('Auto-save failed:', e);
      setAutoSavingProjects(prev => {
        const next = new Set(prev);
        next.delete(selectedProject.id);
        return next;
      });
    }
  }, [selectedProject, formData]);

  // ── Switch active template ─────────────────────────────────────────────────
  const switchTemplate = useCallback(async (templateId) => {
    setActiveTemplateId(templateId);
    try {
      const tpl = await templatesApi.get(templateId);
      setActiveTemplate(tpl);
      setActiveFieldConfig(tpl.field_config || []);
      
      // If a project is selected, preserve its form data
      // Otherwise, initialize fresh form data for this template
      if (!selectedProject) {
        setFormData(buildInitialFormData(tpl.field_config));
      }
      // If project is selected, formData persists (it's in the project's form_data)
    } catch (e) {
      setApiError(e.message);
      return;
    }
    setPdfUrl(null);
    setCurrentEntryId(null);
    setCurrentEntryName('');
    setSaveEntryName('');
  }, [selectedProject]);

  // ── Project CRUD ───────────────────────────────────────────────────────────
  const handleCreateProject = async () => {
    const name = newProjectName.trim();
    if (!name) return;
    try {
      const project = await projectsApi.create(name);
      setProjects(prev => [project, ...prev]);
      setNewProjectName('');
      setSelectedProject(project);
      // Project is created with form_data initialized by backend
      // Form loading is handled by the useEffect that listens to selectedProject
      setCurrentEntryId(null);
      setCurrentEntryName('');
      setSaveEntryName('');
      setPdfUrl(null);
    } catch (e) { setApiError(e.message); }
  };

  const handleDeleteProject = async (project) => {
    if (!window.confirm(`Projekt "${project.name}" und alle Einträge löschen?`)) return;
    try {
      await projectsApi.delete(project.id);
      setProjects(prev => prev.filter(p => p.id !== project.id));
      if (selectedProject?.id === project.id) {
        setSelectedProject(null);
        setEntries([]);
        setFormData({});
      }
    } catch (e) { setApiError(e.message); }
  };

  // ── Save project form data ──────────────────────────────────────────────────
  const handleSaveProject = async () => {
    if (!selectedProject) { alert('Bitte zuerst ein Projekt auswählen.'); return; }
    alert('✓ Projekt wird automatisch gespeichert!');
  };

  // ── Entry CRUD ─────────────────────────────────────────────────────────────
  const handleSaveEntry = async () => {
    if (!selectedProject) { alert('Bitte zuerst ein Projekt auswählen.'); return; }
    const name = saveEntryName.trim() || `Eintrag ${new Date().toLocaleDateString('de-DE')}`;
    try {
      if (currentEntryId) {
        const updated = await entriesApi.update(selectedProject.id, currentEntryId, {
          name,
          field_values: formData,
        });
        setEntries(prev => prev.map(e => e.id === updated.id ? updated : e));
        setCurrentEntryName(updated.name);
      } else {
        const entry = await entriesApi.create(selectedProject.id, name, activeTemplateId, formData);
        setEntries(prev => [entry, ...prev]);
        setCurrentEntryId(entry.id);
        setCurrentEntryName(entry.name);
        setSaveEntryName('');
      }
    } catch (e) { setApiError(e.message); }
  };

  const handleLoadEntry = async (entry) => {
    if (entry.template_id !== activeTemplateId) {
      await switchTemplate(entry.template_id);
    }
    setFormData(entry.field_values);
    setCurrentEntryId(entry.id);
    setCurrentEntryName(entry.name);
    setSaveEntryName(entry.name);
    setPdfUrl(null);
  };

  const handleDeleteEntry = async (entry) => {
    if (!window.confirm(`Eintrag "${entry.name}" löschen?`)) return;
    try {
      await entriesApi.delete(selectedProject.id, entry.id);
      setEntries(prev => prev.filter(e => e.id !== entry.id));
      if (currentEntryId === entry.id) {
        setCurrentEntryId(null);
        setCurrentEntryName('');
        setSaveEntryName('');
      }
    } catch (e) { setApiError(e.message); }
  };

  const handleNewForm = () => {
    // If a project is selected, reset to the project's saved form data
    // Otherwise, reset to template defaults
    if (selectedProject && selectedProject.form_data) {
      setFormData(selectedProject.form_data);
    } else {
      setFormData(buildInitialFormData(activeFieldConfig));
    }
    setCurrentEntryId(null);
    setCurrentEntryName('');
    setSaveEntryName('');
    setPdfUrl(null);
  };

  // ── Template upload / delete ───────────────────────────────────────────────
  const handleTemplateUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const tpl = await templatesApi.upload(file);
      setTemplates(prev => [...prev, tpl]);
      alert(`Template "${tpl.name}" erfolgreich hinzugefügt!`);
    } catch (err) { setApiError(err.message); }
    e.target.value = '';
  };

  const handleDeleteTemplate = async (tpl) => {
    if (tpl.is_builtin) { alert('Eingebaute Templates können nicht gelöscht werden.'); return; }
    if (!window.confirm(`Template "${tpl.name}" löschen?`)) return;
    try {
      await templatesApi.delete(tpl.id);
      setTemplates(prev => prev.filter(t => t.id !== tpl.id));
      if (activeTemplateId === tpl.id) switchTemplate(BUILTIN_TEMPLATE_ID);
    } catch (e) { setApiError(e.message); }
  };

  // ── PDF generation ─────────────────────────────────────────────────────────
  const handleInputChange = (code, value) => {
    setFormData(prev => ({ ...prev, [code]: value }));
  };

  const updatePdf = async () => {
    try {
      if (!activeTemplate || !activeTemplate.pdf_definition) {
        alert('Template PDF definition not loaded');
        return;
      }
      
      // Process the template: replace placeholders with form data
      const processedPdf = processTemplate(activeTemplate.pdf_definition, formData, activeTemplateId);
      
      const pdfDocGenerator = pdfMake.createPdf(processedPdf);
      const pdfBuffer = await pdfDocGenerator.getBuffer();
      const blob = new Blob([pdfBuffer], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
      setPdfUrl(url);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Fehler beim Generieren der PDF. Bitte überprüfen Sie Ihre Eingaben.');
    }
  };

  const handleDownload = () => {
    try {
      if (!activeTemplate || !activeTemplate.pdf_definition) {
        alert('Template PDF definition not loaded');
        return;
      }
      
      const processedPdf = processTemplate(activeTemplate.pdf_definition, formData, activeTemplateId);
      const filename = `${activeTemplate.name}_${formData.F_zc2N || 'Dokument'}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdfMake.createPdf(processedPdf).download(filename);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Fehler beim Herunterladen der PDF.');
    }
  };

  // ── Field renderer ─────────────────────────────────────────────────────────
  const renderField = (field) => {
    const conditionMet = typeof field.condition === 'function'
      ? field.condition(formData)
      : field.condition
        ? evalCondition(field.condition, formData)
        : true;
    if (!conditionMet) return null;

    const value = formData[field.code] || '';
    const isEmpty = !value || (typeof value === 'string' && value.trim() === '');
    const isRequired = field.required && conditionMet;

    let dynamicHelpText = field.helpText;
    if (field.showCalculation && field.code === 'I_5jBb' && formData.I_5jBb && formData.M_zUo9) {
      const daysToAdd = formData.M_zUo9 === 'Schlussrechnung' ? 29 : 20;
      const calculatedDeadline = calculatePaymentDeadline(formData.I_5jBb, formData.M_zUo9);
      const deadlineFormatted = formatDateDE(calculatedDeadline);
      dynamicHelpText = `Zahlungsfrist: +${daysToAdd} Tage = ${deadlineFormatted}`;
    }

    return (
      <div key={field.code} className={`form-group ${isRequired && isEmpty ? 'required-empty' : ''}`}>
        <label htmlFor={field.code}>
          {field.label}
          {isRequired && <span className="required-indicator"> *</span>}
          {dynamicHelpText && <span className="help-text"> ({dynamicHelpText})</span>}
        </label>

        {field.type === 'text' && (
          <input id={field.code} type="text" value={value}
            onChange={e => handleInputChange(field.code, e.target.value)}
            onBlur={saveProjectToBackend}
            placeholder={field.placeholder} disabled={field.calculated} />
        )}
        {field.type === 'number' && (
          <input id={field.code} type="number" value={value}
            onChange={e => handleInputChange(field.code, e.target.value)}
            onBlur={saveProjectToBackend}
            placeholder={field.placeholder} min={field.min} />
        )}
        {field.type === 'date' && (
          <input id={field.code} type="date" value={value}
            onChange={e => handleInputChange(field.code, e.target.value)}
            onBlur={saveProjectToBackend}
            disabled={field.calculated} />
        )}
        {field.type === 'select' && (
          <select id={field.code} value={value}
            onChange={e => handleInputChange(field.code, e.target.value)}
            onBlur={saveProjectToBackend}>
            <option value="">Bitte wählen...</option>
            {(field.options || []).map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        )}
      </div>
    );
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="app-shell" style={{ userSelect: isResizing ? 'none' : 'auto' }}>

      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside className="sidebar" style={{ width: `${sidebarWidth}px` }}>

        {/* Projects */}
        <div className="sidebar-section">
          <h3>Projekte</h3>
          {!apiConnected && (
            <div className="api-error-badge">⚠ Backend nicht verbunden</div>
          )}
          <div className="sidebar-input-row">
            <input
              type="text"
              placeholder="Neues Projekt..."
              value={newProjectName}
              onChange={e => setNewProjectName(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleCreateProject()}
            />
            <button onClick={handleCreateProject} className="btn-icon" title="Erstellen">+</button>
          </div>
          <ul className="sidebar-list">
            {projects.map(p => (
              <li key={p.id}
                className={`sidebar-list-item ${selectedProject?.id === p.id ? 'active' : ''}`}
                onClick={() => setSelectedProject(p)}>
                <span className="item-label">{p.name}</span>
                <button className="btn-icon-danger"
                  onClick={e => { e.stopPropagation(); handleDeleteProject(p); }}>×</button>
              </li>
            ))}
            {projects.length === 0 && <li className="sidebar-empty">Noch keine Projekte</li>}
          </ul>
        </div>

        {/* Templates */}
        <div className="sidebar-section">
          <h3>Templates</h3>
          <ul className="sidebar-list">
            {templates.map(t => (
              <li key={t.id}
                className={`sidebar-list-item ${activeTemplateId === t.id ? 'active' : ''}`}
                onClick={() => switchTemplate(t.id)}>
                <span className="item-label">
                  {t.name}
                  {t.is_builtin && <span className="badge-builtin">built-in</span>}
                </span>
                {!t.is_builtin && (
                  <button className="btn-icon-danger"
                    onClick={ev => { ev.stopPropagation(); handleDeleteTemplate(t); }}>×</button>
                )}
              </li>
            ))}
          </ul>
          <label className="btn-upload">
            + Template hochladen
            <input type="file" accept=".json" onChange={handleTemplateUpload} hidden />
          </label>
        </div>

      </aside>
      <div className="sidebar-resizer" onMouseDown={handleMouseDown} />

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="main-content">

        {apiError && (
          <div className="api-error-banner">
            {apiError}
            <button onClick={() => setApiError(null)}>✕</button>
          </div>
        )}

        <div className="container">

          {/* Form */}
          <div className="form-section">
            <div className="form-header">
              <h2>
                {selectedProject ? selectedProject.name : activeTemplate?.name || activeTemplateId}
              </h2>
            </div>

            <form onSubmit={e => e.preventDefault()}>
              {!activeTemplate && apiConnected && (
                <div className="empty-form-state">
                  <h3>Kein Template geladen</h3>
                  <p>Bitte laden Sie zuerst ein Template über die Sidebar → "Templates" → "+ Template hochladen" hoch.</p>
                  <p>Siehe <strong>TEMPLATES.md</strong> für die Dokumentation zur Template-Erstellung.</p>
                </div>
              )}
              {activeFieldConfig.map(field => renderField(field))}

              {/* Auto-save indicator */}
              {selectedProject && (
                <div className="auto-save-status">
                  {autoSavingProjects.has(selectedProject.id) ? (
                    <span className="saving">💾 Speichern...</span>
                  ) : (
                    <span className="saved">✓ Auto-speichert</span>
                  )}
                </div>
              )}
              {!selectedProject && apiConnected && activeTemplate && (
                <p className="hint-text">← Projekt auswählen um Formulardaten zu speichern</p>
              )}

              {/* PDF generation buttons */}
              <div className="button-group">
                <button type="button" onClick={updatePdf} className="btn-primary">
                  Vorschau Generieren
                </button>
                <button type="button" onClick={handleDownload} className="btn-secondary">
                  PDF Herunterladen
                </button>
              </div>
            </form>
          </div>

          {/* PDF preview */}
          <div className="pdf-section">
            <h2>PDF Vorschau</h2>
            {pdfUrl ? (
              <iframe
                src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0`}
                title="PDF Preview"
                width="100%"
                height="800px"
              />
            ) : (
              <div className="empty-preview">
                <p>Klicken Sie auf "Vorschau Generieren" um Ihr Dokument zu sehen</p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;
