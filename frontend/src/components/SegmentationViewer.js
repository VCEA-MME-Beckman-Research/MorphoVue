import React, { useEffect, useRef, useState } from 'react';
import vtkGenericRenderWindow from 'vtk.js/Sources/Rendering/Misc/GenericRenderWindow';
import vtkNrrdReader from 'vtk.js/Sources/IO/Misc/NrrdReader';
import vtkColorTransferFunction from 'vtk.js/Sources/Rendering/Core/ColorTransferFunction';
import vtkPiecewiseFunction from 'vtk.js/Sources/Common/DataModel/PiecewiseFunction';
import vtkVolume from 'vtk.js/Sources/Rendering/Core/Volume';
import vtkVolumeMapper from 'vtk.js/Sources/Rendering/Core/VolumeMapper';
import vtkVolumeProperty from 'vtk.js/Sources/Rendering/Core/VolumeProperty';

// Minimal 3D volume viewer for NRRD label masks (and optional base volume)
export default function SegmentationViewer({ volumeUrl = null, maskUrl, height = 500 }) {
  const containerRef = useRef(null);
  const grwRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!containerRef.current || !maskUrl) return;

    if (!grwRef.current) {
      grwRef.current = vtkGenericRenderWindow.newInstance({ background: [0.98, 0.98, 0.99] });
      grwRef.current.setContainer(containerRef.current);
      grwRef.current.resize();
    }

    const grw = grwRef.current;
    const renderer = grw.getRenderer();
    const renderWindow = grw.getRenderWindow();

    renderer.removeAllViewProps();

    const readers = [];

    const addVolumeFromNrrd = async (url, isLabel = false) => {
      const reader = vtkNrrdReader.newInstance();
      readers.push(reader);
      await reader.setUrl(url, { loadData: true });
      const data = reader.getOutputData();

      const mapper = vtkVolumeMapper.newInstance();
      mapper.setSampleDistance(1.0);
      mapper.setInputData(data);
      if (isLabel) {
        mapper.setBlendModeToMaximumIntensity();
      }

      const ctf = vtkColorTransferFunction.newInstance();
      const ofun = vtkPiecewiseFunction.newInstance();
      if (isLabel) {
        // Simple categorical coloring for label values
        ctf.addRGBPoint(0, 0.0, 0.0, 0.0);
        ctf.addRGBPoint(1, 0.85, 0.1, 0.1);
        ctf.addRGBPoint(2, 0.1, 0.7, 0.2);
        ctf.addRGBPoint(3, 0.1, 0.4, 0.9);
        ctf.addRGBPoint(4, 0.9, 0.4, 0.1);
        ctf.addRGBPoint(5, 0.7, 0.2, 0.7);
        ofun.addPoint(0, 0.0);
        ofun.addPoint(1, 0.6);
        ofun.addPoint(2, 0.6);
        ofun.addPoint(3, 0.6);
        ofun.addPoint(4, 0.6);
        ofun.addPoint(5, 0.6);
      } else {
        // Greyscale for base CT
        ctf.addRGBPoint(-1000, 0.0, 0.0, 0.0);
        ctf.addRGBPoint(0, 0.5, 0.5, 0.5);
        ctf.addRGBPoint(1000, 1.0, 1.0, 1.0);
        ofun.addPoint(-1000, 0.0);
        ofun.addPoint(0, 0.1);
        ofun.addPoint(1000, 0.9);
      }

      const volProp = vtkVolumeProperty.newInstance();
      volProp.setIndependentComponents(true);
      volProp.setScalarOpacity(0, ofun);
      volProp.setRGBTransferFunction(0, ctf);
      volProp.setInterpolationTypeToLinear();
      if (isLabel) volProp.setShade(false);

      const volume = vtkVolume.newInstance();
      volume.setMapper(mapper);
      volume.setProperty(volProp);

      renderer.addVolume(volume);
    };

    (async () => {
      try {
        if (volumeUrl) await addVolumeFromNrrd(volumeUrl, false);
        await addVolumeFromNrrd(maskUrl, true);
        renderer.resetCamera();
        renderWindow.render();
      } catch (e) {
        setError('Failed to load NRRD data');
        // eslint-disable-next-line no-console
        console.error(e);
      }
    })();

    return () => {
      // Keep viewer instance to allow quick prop updates; cleanup on unmount only
    };
  }, [volumeUrl, maskUrl]);

  return (
    <div className="bg-gray-100 rounded-lg" style={{ height }}>
      {error ? (
        <div className="h-full flex items-center justify-center text-sm text-red-600">{error}</div>
      ) : (
        <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      )}
    </div>
  );
}
