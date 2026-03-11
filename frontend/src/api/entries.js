import { api } from './client';

export const entriesApi = {
  list:   (projectId)                          => api.get(`/api/projects/${projectId}/entries/`),
  get:    (projectId, entryId)                 => api.get(`/api/projects/${projectId}/entries/${entryId}`),
  create: (projectId, name, templateId, fieldValues) =>
    api.post(`/api/projects/${projectId}/entries/`, { name, template_id: templateId, field_values: fieldValues }),
  update: (projectId, entryId, data)           => api.put(`/api/projects/${projectId}/entries/${entryId}`, data),
  delete: (projectId, entryId)                 => api.delete(`/api/projects/${projectId}/entries/${entryId}`),
};
