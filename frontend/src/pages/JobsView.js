import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

function JobsView() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [updatingJob, setUpdatingJob] = useState(null);

  useEffect(() => {
    loadJobs();
    // Refresh jobs every 30 seconds
    const interval = setInterval(loadJobs, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadJobs = async () => {
    try {
      const response = await api.getJobs();
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to load jobs', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (jobId, status, slurmId = '') => {
    setUpdatingJob(jobId);
    try {
      await api.updateJobStatus(jobId, {
        status,
        slurm_id: slurmId || null
      });
      loadJobs();
      alert('Job status updated');
    } catch (error) {
      console.error('Failed to update job status', error);
      alert('Failed to update job status');
    } finally {
      setUpdatingJob(null);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Kamiak Jobs</h1>
        <button
          onClick={loadJobs}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
        >
          Refresh
        </button>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs</h3>
          <p className="mt-1 text-sm text-gray-500">Submit a batch to Kamiak to get started.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map(job => (
            <div key={job.id} className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h3 className="text-lg font-medium text-gray-900">
                      Job {job.id.substring(0, 8)}
                    </h3>
                    <span className={`ml-3 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                  </div>
                  
                  <div className="mt-2 text-sm text-gray-600">
                    <p><strong>Scans:</strong> {job.scan_ids.length} scan(s)</p>
                    <p><strong>Submitted:</strong> {new Date(job.submitted_at).toLocaleString()}</p>
                    {job.slurm_id && (
                      <p><strong>SLURM ID:</strong> {job.slurm_id}</p>
                    )}
                    {job.completed_at && (
                      <p><strong>Completed:</strong> {new Date(job.completed_at).toLocaleString()}</p>
                    )}
                  </div>

                  {selectedJob === job.id && (
                    <div className="mt-4 space-y-2">
                      <h4 className="font-medium text-gray-900">Scan IDs:</h4>
                      <div className="bg-gray-50 p-3 rounded text-xs font-mono">
                        {job.scan_ids.join(', ')}
                      </div>
                    </div>
                  )}
                </div>

                <div className="ml-4 flex-shrink-0 space-y-2">
                  <button
                    onClick={() => setSelectedJob(selectedJob === job.id ? null : job.id)}
                    className="block w-full text-sm text-primary-600 hover:text-primary-700"
                  >
                    {selectedJob === job.id ? 'Hide Details' : 'Show Details'}
                  </button>
                  
                  {job.status === 'pending' && (
                    <div className="space-y-2">
                      <input
                        type="text"
                        placeholder="SLURM Job ID"
                        className="block w-full text-sm px-2 py-1 border border-gray-300 rounded"
                        id={`slurm-${job.id}`}
                      />
                      <button
                        onClick={() => {
                          const slurmId = document.getElementById(`slurm-${job.id}`).value;
                          handleUpdateStatus(job.id, 'running', slurmId);
                        }}
                        disabled={updatingJob === job.id}
                        className="block w-full text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                      >
                        Mark Running
                      </button>
                    </div>
                  )}
                  
                  {job.status === 'running' && (
                    <button
                      onClick={() => handleUpdateStatus(job.id, 'completed')}
                      disabled={updatingJob === job.id}
                      className="block w-full text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                    >
                      Mark Completed
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default JobsView;

