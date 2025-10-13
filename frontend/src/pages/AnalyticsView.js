import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

function AnalyticsView() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [scans, setScans] = useState([]);
  const [allQuantResults, setAllQuantResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    try {
      const [projectRes, scansRes] = await Promise.all([
        api.getProject(projectId),
        api.getProjectScans(projectId)
      ]);
      
      setProject(projectRes.data);
      setScans(scansRes.data);
      
      // Load quantification results for all scans
      const completedScans = scansRes.data.filter(s => s.processing_status === 'completed');
      const quantPromises = completedScans.map(async scan => {
        const segmentations = await api.getScanSegmentations(scan.id);
        if (segmentations.data.length > 0) {
          const quant = await api.getQuantificationResults(segmentations.data[0].id);
          return quant.data;
        }
        return [];
      });
      
      const quantResults = await Promise.all(quantPromises);
      setAllQuantResults(quantResults.flat());
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const getStatusDistribution = () => {
    const statusCounts = scans.reduce((acc, scan) => {
      acc[scan.processing_status] = (acc[scan.processing_status] || 0) + 1;
      return acc;
    }, {});

    return {
      labels: Object.keys(statusCounts),
      datasets: [{
        data: Object.values(statusCounts),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'
        ],
      }]
    };
  };

  const getOrganVolumeData = () => {
    const organVolumes = {};
    
    allQuantResults.forEach(result => {
      if (!organVolumes[result.organ_name]) {
        organVolumes[result.organ_name] = [];
      }
      organVolumes[result.organ_name].push(result.volume);
    });

    const avgVolumes = {};
    Object.keys(organVolumes).forEach(organ => {
      const volumes = organVolumes[organ];
      avgVolumes[organ] = volumes.reduce((a, b) => a + b, 0) / volumes.length;
    });

    return {
      labels: Object.keys(avgVolumes),
      datasets: [{
        label: 'Average Volume (mm³)',
        data: Object.values(avgVolumes),
        backgroundColor: '#3B82F6',
      }]
    };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  const statusData = getStatusDistribution();
  const volumeData = allQuantResults.length > 0 ? getOrganVolumeData() : null;

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link to={`/project/${projectId}`} className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
          ← Back to Project
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Analytics: {project?.name}</h1>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3 mb-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Scans</dt>
                  <dd className="text-3xl font-semibold text-gray-900">{scans.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                  <dd className="text-3xl font-semibold text-gray-900">
                    {scans.filter(s => s.processing_status === 'completed').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Segmentations</dt>
                  <dd className="text-3xl font-semibold text-gray-900">{allQuantResults.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Scan Status Distribution</h2>
          {scans.length > 0 ? (
            <div className="max-w-sm mx-auto">
              <Pie data={statusData} />
            </div>
          ) : (
            <p className="text-sm text-gray-500">No data available</p>
          )}
        </div>

        {/* Organ Volume */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Average Organ Volume</h2>
          {volumeData ? (
            <Bar
              data={volumeData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    display: false
                  },
                  title: {
                    display: false
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Volume (mm³)'
                    }
                  }
                }
              }}
            />
          ) : (
            <p className="text-sm text-gray-500">No quantification data available</p>
          )}
        </div>
      </div>

      {/* Quantification Table */}
      {allQuantResults.length > 0 && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">All Quantification Results</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Organ
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Volume (mm³)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Surface Area (mm²)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Centroid
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {allQuantResults.map((result, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {result.organ_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {result.volume.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {result.surface_area.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono text-xs">
                      [{result.centroid.map(c => c.toFixed(1)).join(', ')}]
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyticsView;

