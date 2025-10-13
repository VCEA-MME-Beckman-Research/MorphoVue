import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';

function ReviewView() {
  const { scanId } = useParams();
  const [scan, setScan] = useState(null);
  const [segmentations, setSegmentations] = useState([]);
  const [quantResults, setQuantResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSegmentation, setSelectedSegmentation] = useState(null);

  useEffect(() => {
    loadData();
  }, [scanId]);

  const loadData = async () => {
    try {
      const [scanRes, segRes] = await Promise.all([
        api.getScan(scanId),
        api.getScanSegmentations(scanId)
      ]);
      
      setScan(scanRes.data);
      setSegmentations(segRes.data);
      
      if (segRes.data.length > 0) {
        loadQuantificationResults(segRes.data[0].id);
        setSelectedSegmentation(segRes.data[0]);
      }
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  const loadQuantificationResults = async (segmentationId) => {
    try {
      const response = await api.getQuantificationResults(segmentationId);
      setQuantResults(response.data);
    } catch (error) {
      console.error('Failed to load quantification results', error);
    }
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
        <Link to={`/project/${scan?.project_id}`} className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
          ← Back to Project
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Review: {scan?.filename}</h1>
      </div>

      {/* Content */}
      {segmentations.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No segmentation results</h3>
          <p className="mt-1 text-sm text-gray-500">
            This scan hasn't been processed yet. Submit it for processing on Kamiak.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 3D Viewer - Placeholder */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">3D Visualization</h2>
            <div className="bg-gray-100 rounded-lg flex items-center justify-center" style={{ height: '500px' }}>
              <div className="text-center">
                <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">
                  VTK.js 3D viewer will be displayed here
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Shows CT volume with segmentation overlay
                </p>
                <div className="mt-4">
                  <a
                    href="https://kitware.github.io/vtk-js/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 text-sm"
                  >
                    VTK.js Documentation →
                  </a>
                </div>
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-600">
              <p><strong>Model:</strong> {selectedSegmentation?.model_version}</p>
              <p><strong>Created:</strong> {new Date(selectedSegmentation?.created_at).toLocaleString()}</p>
            </div>
          </div>

          {/* Quantification Results */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Quantification Results</h2>
            
            {quantResults.length === 0 ? (
              <p className="text-sm text-gray-500">No quantification data available</p>
            ) : (
              <div className="space-y-4">
                {quantResults.map((result) => (
                  <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">
                      {result.organ_name}
                    </h3>
                    <dl className="text-sm space-y-1">
                      <div className="flex justify-between">
                        <dt className="text-gray-500">Volume:</dt>
                        <dd className="text-gray-900 font-medium">
                          {result.volume.toFixed(2)} mm³
                        </dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-500">Surface Area:</dt>
                        <dd className="text-gray-900 font-medium">
                          {result.surface_area.toFixed(2)} mm²
                        </dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-500">Centroid:</dt>
                        <dd className="text-gray-900 text-xs">
                          [{result.centroid.map(c => c.toFixed(1)).join(', ')}]
                        </dd>
                      </div>
                    </dl>
                  </div>
                ))}
              </div>
            )}

            {/* Download Button */}
            {selectedSegmentation && (
              <div className="mt-6">
                <button
                  className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  onClick={() => window.open(selectedSegmentation.mask_url, '_blank')}
                >
                  Download Mask (NRRD)
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Open in 3D Slicer for detailed review
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ReviewView;

