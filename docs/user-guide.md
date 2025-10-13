# User Guide - MorphoVue CT Tick ML Platform

Complete guide for researchers using MorphoVue.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Projects](#creating-projects)
3. [Uploading Scans](#uploading-scans)
4. [Annotating Data](#annotating-data)
5. [Submitting Jobs](#submitting-jobs)
6. [Reviewing Results](#reviewing-results)
7. [Analytics](#analytics)
8. [3D Slicer Integration](#3d-slicer-integration)

## Getting Started

### Accessing MorphoVue

1. Open your web browser
2. Navigate to: https://your-project-id.web.app
3. Sign in with your credentials

First-time users:
- Contact your administrator for account creation
- You will receive login credentials via email

### Dashboard Overview

After login, you'll see the main dashboard with:
- **Projects**: Your research projects
- **Batch Submit**: Submit scans for processing
- **Jobs**: Track Kamiak job status

## Creating Projects

### Step 1: Create New Project

1. Click "+ New Project" on the dashboard
2. Enter project details:
   - **Name**: Descriptive project name (e.g., "Tick Study 2024")
   - **Description**: Optional project notes
3. Click "Create"

### Step 2: Project Organization

Best practices:
- One project per research study
- Use descriptive names
- Add detailed descriptions for team collaboration

## Uploading Scans

### Supported Formats

- **TIFF files** (.tiff, .tif)
- Multi-page TIFF files (stacked slices)
- Individual slices will be extracted automatically

### Upload Process

1. Open your project
2. Click "+ Upload Scan"
3. Choose upload method:
   - **Drag and drop**: Drag TIFF file to upload area
   - **Click to browse**: Select file from your computer
4. Wait for upload to complete
5. Scan appears in project scan list

### Upload Tips

- **File size**: Typical CT scans are 50-500 MB
- **Internet**: Stable connection recommended
- **Progress**: Upload progress bar shows status
- **Multiple scans**: Upload one at a time

## Annotating Data

### Opening Label Studio

1. In your project, click scan name or "Annotate" button
2. Label Studio opens (embedded or new tab)
3. You'll see the annotation interface

### Annotation Types

#### Bounding Box Annotation (YOLOv10 Training)

Used for object detection:

1. Select Rectangle tool
2. Draw box around entire tick
3. Label as "tick"
4. Repeat for each slice
5. Click "Submit" to save

#### Segmentation Annotation (MONAI Training)

Used for detailed organ segmentation:

1. Select Brush or Polygon tool
2. Carefully outline organs:
   - Digestive tract
   - Reproductive organs
   - Neural tissue
3. Use different colors for each organ
4. Submit when complete

### Annotation Best Practices

- **Consistency**: Use same labeling approach across all scans
- **Accuracy**: Take time to be precise
- **Coverage**: Annotate all visible structures
- **Save frequently**: Submit annotations regularly
- **Review**: Double-check before marking complete

### Marking Complete

After annotation:
1. Return to MorphoVue
2. Click "Mark as Annotated"
3. Scan status updates to "annotated"

## Submitting Jobs

### When to Submit

Submit scans when:
- Annotation is complete
- Multiple scans ready for processing
- You have access to Kamiak

### Batch Submission Process

#### Step 1: Select Scans

1. Go to "Batch Submit" page
2. Select your project
3. Check boxes for scans to process
4. Click "Generate Job Script"

#### Step 2: Download Script

The interface provides:
- **Job script**: SLURM batch script
- **Instructions**: Step-by-step guide
- **Scan IDs**: List of scans to process

#### Step 3: Submit to Kamiak

Follow the displayed instructions:

```bash
# 1. Download script
wget '<script_url>' -O job_abc123.sh

# 2. SSH to Kamiak
ssh <username>@kamiak.wsu.edu

# 3. Copy script
cp ~/Downloads/job_abc123.sh ~/MorphoVue/ml-pipeline/

# 4. Navigate to directory
cd ~/MorphoVue/ml-pipeline

# 5. Submit job
sbatch job_abc123.sh
```

#### Step 4: Note SLURM Job ID

After submission, note the SLURM job ID:
```
Submitted batch job 1234567
```

#### Step 5: Update Status (Optional)

In MorphoVue Jobs page:
1. Find your job
2. Enter SLURM Job ID
3. Click "Mark Running"

### Processing Time

Typical processing times:
- Single scan: 10-30 minutes
- Batch of 10 scans: 2-5 hours
- Depends on scan size and GPU availability

## Reviewing Results

### When Results Are Available

Results appear when:
- Kamiak job completes successfully
- Data is uploaded to Firebase
- Scan status shows "completed"

### Accessing Results

1. Open your project
2. Click scan name or "Review" button
3. View segmentation results

### Result Components

#### 3D Visualization

- **Interactive viewer**: Rotate and zoom 3D model
- **Slice views**: Axial, sagittal, coronal
- **Overlay**: Segmentation mask overlay
- **Model info**: Model version and creation date

#### Quantification Results

For each segmented organ:
- **Volume**: Organ volume in mm³
- **Surface Area**: Surface area in mm²
- **Centroid**: 3D center coordinates
- **Bounding Box**: Spatial extent

#### Download Options

- **Mask File**: Download NRRD file
- **Statistics**: Export as CSV/JSON
- **3D Model**: Export for 3D Slicer

## Analytics

### Project Analytics

Access analytics:
1. Open project
2. Click "Analytics" button

### Available Visualizations

#### Scan Status Distribution
- Pie chart showing scan statuses
- Uploaded, annotating, processing, completed

#### Organ Volume Distribution
- Bar chart of average organ volumes
- Compare across multiple scans

#### Processing Statistics
- Total scans processed
- Success rate
- Average processing time

### Exporting Data

- **CSV Export**: Download quantification data
- **Charts**: Save as images
- **Reports**: Generate summary reports

## 3D Slicer Integration

### Why Use 3D Slicer?

- Advanced 3D visualization
- Manual segmentation correction
- Detailed quantification
- Research-grade analysis

### Opening in 3D Slicer

#### Step 1: Download Files

From MorphoVue Review page:
1. Download CT scan (TIFF)
2. Download segmentation mask (NRRD)

#### Step 2: Load in 3D Slicer

1. Open 3D Slicer
2. Load "Tick Segmentation Review" module
3. Enter Scan ID
4. Click "Load from Firebase"
5. Select downloaded files

#### Step 3: Review and Edit

- Use 3D view to inspect segmentation
- Zoom and rotate
- Use Segment Editor to correct mistakes
- Compute updated statistics

#### Step 4: Export Corrections

1. Click "Upload Corrected Mask"
2. Save to local file
3. Upload to MorphoVue manually

### 3D Slicer Features

**Visualization:**
- Volume rendering
- Multi-planar reconstruction
- 3D surface models

**Editing:**
- Paint/Erase tools
- Threshold segmentation
- Smoothing and filling

**Analysis:**
- Precise volume calculation
- Distance measurements
- Cross-sectional analysis

## Common Workflows

### Workflow 1: New Study

1. Create project
2. Upload all scans
3. Annotate systematically
4. Submit batch when ready
5. Review results
6. Download for publication

### Workflow 2: Iterative Training

1. Annotate initial scans
2. Submit for processing
3. Review model performance
4. Correct errors in 3D Slicer
5. Re-annotate with corrections
6. Submit improved dataset

### Workflow 3: Quality Control

1. Process batch of scans
2. Review all results
3. Identify problematic segmentations
4. Manually correct in 3D Slicer
5. Re-process if needed
6. Export final data

## Tips and Tricks

### Annotation Tips

- **Zoom in**: Use zoom for precise boundaries
- **Multiple passes**: Rough outline first, refine later
- **Shortcuts**: Learn keyboard shortcuts
- **Breaks**: Take breaks for eye health

### Processing Tips

- **Batch size**: 5-10 scans per batch optimal
- **Off-peak hours**: Submit during evenings/weekends
- **Monitor**: Check job status regularly
- **Logs**: Review Kamiak logs for errors

### Visualization Tips

- **Contrast**: Adjust window/level for better visualization
- **Colors**: Use distinct colors for each organ
- **Overlays**: Toggle overlay on/off for comparison
- **Screenshots**: Capture images for presentations

## Troubleshooting

### Upload Issues

**Problem**: Upload fails or stalls
**Solution**:
- Check internet connection
- Try smaller file
- Refresh page and retry
- Clear browser cache

### Annotation Issues

**Problem**: Label Studio doesn't load
**Solution**:
- Refresh page
- Check browser console for errors
- Try different browser
- Contact administrator

### Processing Issues

**Problem**: Job fails on Kamiak
**Solution**:
- Check Kamiak logs
- Verify Firebase credentials
- Check scan format
- Re-submit with fewer scans

### Results Issues

**Problem**: Results don't appear
**Solution**:
- Wait for job completion
- Refresh page
- Check job status
- Check Firebase storage

## Getting Help

### Documentation

- **User Guide**: This document
- **Kamiak Guide**: HPC-specific instructions
- **API Docs**: For developers
- **Video Tutorials**: Coming soon

### Support Channels

- **Email**: support@morphovue.org
- **GitHub Issues**: Bug reports
- **Office Hours**: Weekly Q&A sessions
- **Slack**: Team communication

### FAQs

**Q: How long does processing take?**
A: 10-30 minutes per scan, depending on size and GPU availability.

**Q: Can I download raw data?**
A: Yes, all data is downloadable from results page.

**Q: What if segmentation is wrong?**
A: Use 3D Slicer to manually correct and re-upload.

**Q: How much storage do I have?**
A: Contact administrator for quota information.

**Q: Can I collaborate with others?**
A: Yes, multiple users can access shared projects.

## Best Practices

### Data Management

- Organize scans by study/date
- Use consistent naming conventions
- Document annotations
- Back up important results
- Archive completed projects

### Quality Assurance

- Review all segmentations
- Spot-check automated results
- Maintain annotation guidelines
- Regular calibration sessions
- Peer review

### Collaboration

- Share project access with team
- Document decisions in project notes
- Regular team meetings
- Consistent methodology
- Version control for protocols

## Advanced Features

### API Access

For programmatic access:
```python
import requests

API_URL = "https://your-project-id.run.app"
token = "your-auth-token"

# Upload scan programmatically
files = {'file': open('scan.tiff', 'rb')}
data = {'project_id': 'project-123'}
headers = {'Authorization': f'Bearer {token}'}

response = requests.post(
    f"{API_URL}/api/scans/upload",
    files=files,
    data=data,
    headers=headers
)
```

### Batch Processing Scripts

Automate workflows with scripts:
- Bulk upload
- Automated annotation
- Result aggregation

### Custom Models

Train custom models:
- Export annotations
- Train locally or on Kamiak
- Upload custom weights
- Test and deploy

## Appendix

### Keyboard Shortcuts

**Label Studio:**
- `Space`: Pan mode
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Delete`: Delete selected

**3D Slicer:**
- `Ctrl+0`: Reset view
- `F`: Fly to mouse
- `G`: Toggle slice intersections

### File Formats

- **.tiff**: CT scan input
- **.nrrd**: Segmentation masks
- **.json**: Annotations and metadata
- **.csv**: Quantification results

### Glossary

- **ROI**: Region of Interest
- **Segmentation**: Outlining structures
- **Quantification**: Measuring properties
- **SLURM**: Job scheduler on Kamiak
- **YOLO**: Object detection model
- **MONAI**: Medical imaging framework

## Changelog

### Version 1.0.0 (2024)
- Initial release
- Basic workflow support
- Kamiak integration
- 3D Slicer module

---

*Last updated: October 2024*
*For questions, contact: support@morphovue.org*

