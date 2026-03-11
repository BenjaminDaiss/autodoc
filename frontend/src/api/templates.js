import { api } from './client';

export const templatesApi = {
  list: ()     => api.get('/api/templates/'),
  get:  (id)   => api.get(`/api/templates/${id}`),
  delete: (id) => api.delete(`/api/templates/${id}`),

  /**
   * Upload a .json file as a new custom template.
   * @param {File} file - a File object from an <input type="file">
   */
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch('/api/templates/upload', {
      method: 'POST',
      body: formData,
      // Do NOT set Content-Type header – browser sets it with boundary automatically
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Upload failed: ${res.status}`);
    return data;
  },
};
