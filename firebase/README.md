# Firebase Configuration

## Setup

1. Create a Firebase project at https://console.firebase.google.com/

2. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

3. Login to Firebase:
```bash
firebase login
```

4. Initialize Firebase:
```bash
cp .firebaserc.example .firebaserc
# Edit .firebaserc and replace "your-project-id" with your actual project ID
```

5. Download service account key:
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Save as `firebase-credentials.json` (DO NOT commit this file)

## Firestore Schema

### Collections

- **users**: User profiles and roles
- **projects**: Research projects
- **scans**: CT scan metadata
- **annotations**: Label Studio annotation exports
- **segmentations**: MONAI segmentation results
- **quantification_results**: Organ-level statistics
- **kamiak_jobs**: Job tracking for HPC submissions

## Deployment

Deploy all Firebase resources:
```bash
npm run deploy
```

Deploy specific resources:
```bash
npm run deploy:hosting
npm run deploy:firestore
npm run deploy:storage
```

## Local Development

Start Firebase emulators:
```bash
npm run emulators:start
```

This starts:
- Firestore emulator: http://localhost:8080
- Storage emulator: http://localhost:9199
- Auth emulator: http://localhost:9099

