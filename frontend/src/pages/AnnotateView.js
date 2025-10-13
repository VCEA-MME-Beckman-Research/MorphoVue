import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';

const LABEL_STUDIO_URL = process.env.REACT_APP_LABEL_STUDIO_URL || 'http://localhost:8080';

function AnnotateView() {
  const { scanId } = useParams();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScan();
  }, [scanId]);

  const loadScan = async () => {
    try {
      const response = await api.getScan(scanId);
      setScan(response.data);
    } catch (error) {
      console.error('Failed to load scan', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnnotationComplete = async () => {
    try {
      // Update scan status to annotated
      await api.updateScanStatus(scanId, 'annotated');
      alert('Annotations saved successfully!');
    } catch (error) {
      console.error('Failed to update scan status', error);
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Annotate: {scan?.filename}</h1>
            <p className="text-gray-600 mt-1">
              Draw bounding boxes around ticks and segment organs
            </p>
          </div>
          <button
            onClick={handleAnnotationComplete}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Mark as Annotated
          </button>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Annotation Instructions</h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Use Label Studio to draw bounding boxes around ticks (for YOLOv10 training)</li>
          <li>For detailed segmentation, use the brush/polygon tool to outline organs</li>
          <li>Click "Submit" in Label Studio to save your annotations</li>
          <li>Click "Mark as Annotated" above when finished</li>
        </ul>
      </div>

      {/* Label Studio iframe */}
      <div className="bg-white shadow rounded-lg overflow-hidden" style={{ height: '800px' }}>
        <iframe
          src={`${LABEL_STUDIO_URL}/projects`}
          title="Label Studio"
          className="w-full h-full border-0"
          allow="clipboard-read; clipboard-write"
        />
      </div>

      {/* Alternative: Open in new tab */}
      <div className="mt-4 text-center">
        <a
          href={`${LABEL_STUDIO_URL}/projects`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary-600 hover:text-primary-700 text-sm"
        >
          Open Label Studio in new tab →
        </a>
      </div>
    </div>
  );
}

export default AnnotateView;

