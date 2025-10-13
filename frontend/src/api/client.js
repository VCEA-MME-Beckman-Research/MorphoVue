import axios from 'axios';
import { auth } from '../firebase';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // Projects
  createProject: (data) => apiClient.post('/api/projects', data),
  getProjects: () => apiClient.get('/api/projects'),
  getProject: (id) => apiClient.get(`/api/projects/${id}`),
  deleteProject: (id) => apiClient.delete(`/api/projects/${id}`),
  
  // Scans
  uploadScan: (projectId, file, onProgress) => {
    const formData = new FormData();
    formData.append('project_id', projectId);
    formData.append('file', file);
    
    return apiClient.post('/api/scans/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) onProgress(percentCompleted);
      },
    });
  },
  getScan: (id) => apiClient.get(`/api/scans/${id}`),
  getProjectScans: (projectId) => apiClient.get(`/api/projects/${projectId}/scans`),
  updateScanStatus: (id, status) => apiClient.patch(`/api/scans/${id}/status`, { status }),
  getScanDownloadUrl: (id) => apiClient.get(`/api/scans/${id}/download-url`),
  
  // Annotations
  syncAnnotations: (data) => apiClient.post('/api/annotations/sync', data),
  getScanAnnotations: (scanId) => apiClient.get(`/api/scans/${scanId}/annotations`),
  getAnnotationDownloadUrl: (id) => apiClient.get(`/api/annotations/${id}`),
  
  // Jobs
  generateJob: (data) => apiClient.post('/api/jobs/generate', data),
  getJob: (id) => apiClient.get(`/api/jobs/${id}`),
  getJobs: () => apiClient.get('/api/jobs'),
  updateJobStatus: (id, data) => apiClient.post(`/api/jobs/${id}/update`, data),
  
  // Results
  uploadResults: (data) => apiClient.post('/api/results/upload', data),
  getScanSegmentations: (scanId) => apiClient.get(`/api/scans/${scanId}/segmentations`),
  getQuantificationResults: (segmentationId) => 
    apiClient.get(`/api/quantification/${segmentationId}`),
  getSegmentation: (id) => apiClient.get(`/api/segmentations/${id}`),
  
  // Health
  health: () => apiClient.get('/api/health'),
};

export default apiClient;

