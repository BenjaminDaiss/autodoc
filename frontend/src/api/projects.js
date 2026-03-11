import { api } from './client';

export const projectsApi = {
  list:   ()                      => api.get('/api/projects/'),
  get:    (id)                    => api.get(`/api/projects/${id}`),
  create: (name, description='') => api.post('/api/projects/', { name, description }),
  update: (id, data)              => api.put(`/api/projects/${id}`, data),
  delete: (id)                    => api.delete(`/api/projects/${id}`),
};
