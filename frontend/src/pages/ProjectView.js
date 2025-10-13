import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import UploadModal from '../components/UploadModal';

function ProjectView() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    loadProject();
    loadScans();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await api.getProject(projectId);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to load project', error);
    }
  };

  const loadScans = async () => {
    try {
      const response = await api.getProjectScans(projectId);
      setScans(response.data);
    } catch (error) {
      console.error('Failed to load scans', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      uploaded: 'bg-blue-100 text-blue-800',
      annotating: 'bg-yellow-100 text-yellow-800',
      annotated: 'bg-green-100 text-green-800',
      queued: 'bg-purple-100 text-purple-800',
      processing: 'bg-orange-100 text-orange-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link to="/" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
          ← Back to Projects
        </Link>
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{project?.name}</h1>
            {project?.description && (
              <p className="text-gray-600 mt-1">{project.description}</p>
            )}
          </div>
          <div className="flex space-x-3">
            <Link
              to={`/analytics/${projectId}`}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Analytics
            </Link>
            <button
              onClick={() => setShowUploadModal(true)}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              + Upload Scan
            </button>
          </div>
        </div>
      </div>

      {/* Scans Table */}
      {scans.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No scans</h3>
          <p className="mt-1 text-sm text-gray-500">Upload your first CT scan to get started.</p>
          <div className="mt-6">
            <button
              onClick={() => setShowUploadModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              + Upload Scan
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Filename
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Upload Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {scans.map((scan) => (
                <tr key={scan.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {scan.filename}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(scan.processing_status)}`}>
                      {scan.processing_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(scan.upload_timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {scan.file_size ? (scan.file_size / 1024 / 1024).toFixed(2) + ' MB' : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link
                      to={`/annotate/${scan.id}`}
                      className="text-primary-600 hover:text-primary-900 mr-4"
                    >
                      Annotate
                    </Link>
                    <Link
                      to={`/review/${scan.id}`}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      Review
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <UploadModal
          projectId={projectId}
          onClose={() => setShowUploadModal(false)}
          onSuccess={() => {
            setShowUploadModal(false);
            loadScans();
          }}
        />
      )}
    </div>
  );
}

export default ProjectView;

