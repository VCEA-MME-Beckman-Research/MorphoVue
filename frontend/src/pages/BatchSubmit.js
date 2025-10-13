import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

function BatchSubmit() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [scans, setScans] = useState([]);
  const [selectedScans, setSelectedScans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [jobInstructions, setJobInstructions] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadScans();
    }
  }, [selectedProject]);

  const loadProjects = async () => {
    try {
      const response = await api.getProjects();
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to load projects', error);
    }
  };

  const loadScans = async () => {
    try {
      const response = await api.getProjectScans(selectedProject);
      // Filter for annotated scans
      const annotatedScans = response.data.filter(
        scan => scan.processing_status === 'annotated' || scan.processing_status === 'uploaded'
      );
      setScans(annotatedScans);
    } catch (error) {
      console.error('Failed to load scans', error);
    }
  };

  const toggleScanSelection = (scanId) => {
    setSelectedScans(prev =>
      prev.includes(scanId)
        ? prev.filter(id => id !== scanId)
        : [...prev, scanId]
    );
  };

  const handleGenerateJob = async () => {
    if (selectedScans.length === 0) {
      alert('Please select at least one scan');
      return;
    }

    setLoading(true);
    try {
      const response = await api.generateJob({
        scan_ids: selectedScans,
        job_name: 'cttick_pipeline',
        partition: 'gpu',
        time_limit: '02:00:00'
      });
      setJobInstructions(response.data);
    } catch (error) {
      console.error('Failed to generate job', error);
      alert('Failed to generate job script');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Batch Submit to Kamiak</h1>

      {!jobInstructions ? (
        <div className="space-y-6">
          {/* Project Selection */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Select Project</h2>
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">-- Select a project --</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          {/* Scan Selection */}
          {selectedProject && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">
                Select Scans ({selectedScans.length} selected)
              </h2>
              
              {scans.length === 0 ? (
                <p className="text-sm text-gray-500">No annotated scans available in this project</p>
              ) : (
                <div className="space-y-2">
                  {scans.map(scan => (
                    <label
                      key={scan.id}
                      className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedScans.includes(scan.id)}
                        onChange={() => toggleScanSelection(scan.id)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div className="ml-3 flex-1">
                        <span className="text-sm font-medium text-gray-900">
                          {scan.filename}
                        </span>
                        <span className="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {scan.processing_status}
                        </span>
                      </div>
                    </label>
                  ))}
                </div>
              )}

              {scans.length > 0 && (
                <div className="mt-6">
                  <button
                    onClick={handleGenerateJob}
                    disabled={loading || selectedScans.length === 0}
                    className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                  >
                    {loading ? 'Generating...' : 'Generate Job Script'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Instructions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Job Submission Instructions</h2>
            <div className="space-y-4">
              {jobInstructions.instructions.map((instruction, idx) => (
                <div key={idx} className="text-sm text-gray-700">
                  {instruction}
                </div>
              ))}
            </div>
          </div>

          {/* Script */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Job Script</h2>
              <button
                onClick={() => copyToClipboard(jobInstructions.script_content)}
                className="px-3 py-1 text-sm bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                Copy Script
              </button>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs">
              {jobInstructions.script_content}
            </pre>
          </div>

          {/* Download */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Download Script</h2>
            <a
              href={jobInstructions.script_path}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Download {jobInstructions.job_id}.sh
            </a>
          </div>

          {/* Reset */}
          <div className="text-center">
            <button
              onClick={() => {
                setJobInstructions(null);
                setSelectedScans([]);
              }}
              className="text-primary-600 hover:text-primary-700 text-sm"
            >
              ← Submit another batch
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default BatchSubmit;

