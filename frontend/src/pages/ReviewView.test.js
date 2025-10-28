import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ReviewView from './ReviewView';

// Mock api client
jest.mock('../api/client', () => {
  return {
    api: {
      getScan: jest.fn(async () => ({ data: { id: 's1', filename: 'scan.tiff', project_id: 'p1' } })),
      getScanSegmentations: jest.fn(async () => ({ data: [ { id: 'seg1', mask_url: 'segmentations/s1/mask.nrrd', volume_url: null, model_version: 'v1', created_at: new Date().toISOString() } ] })),
      getQuantificationResults: jest.fn(async () => ({ data: [ { id: 'q1', organ_name: 'organ1', volume: 1.23, surface_area: 2.34, centroid: [1,2,3] } ] })),
      getSegmentationDownloadUrl: jest.fn(async () => ({ data: { download_url: 'https://signed.example/mask.nrrd' } })),
    }
  };
});

// Mock SegmentationViewer to avoid VTK heavy init
jest.mock('../components/SegmentationViewer', () => () => <div data-testid="viewer">viewer</div>);

function renderWithRouter(scanId = 's1') {
  return render(
    <MemoryRouter initialEntries={[`/review/${scanId}`]}>
      <Routes>
        <Route path="/review/:scanId" element={<ReviewView />} />
      </Routes>
    </MemoryRouter>
  );
}

test('renders review view with viewer and quant results', async () => {
  renderWithRouter('s1');

  expect(screen.getByText(/Loading/i)).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByTestId('viewer')).toBeInTheDocument();
  });

  expect(screen.getByText(/Quantification Results/i)).toBeInTheDocument();
  expect(screen.getByText(/organ1/i)).toBeInTheDocument();
});
