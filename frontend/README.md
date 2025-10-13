# Frontend - React Application

React frontend for the CT Tick ML Platform.

## Features

- User authentication with Firebase
- Project and scan management
- Label Studio integration for annotations
- Batch job submission to Kamiak HPC
- 3D visualization with VTK.js (placeholder)
- Analytics dashboard with Chart.js

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Firebase credentials and API URL
```

3. Start development server:
```bash
npm start
```

The app will open at http://localhost:3000

## Build for Production

```bash
npm run build
```

This creates an optimized build in the `build/` directory, ready for Firebase Hosting deployment.

## Project Structure

```
src/
├── api/           # API client and endpoints
├── components/    # Reusable React components
├── contexts/      # React contexts (Auth)
├── pages/         # Page components
├── App.js         # Main app component
├── firebase.js    # Firebase configuration
└── index.js       # Entry point
```

## Pages

- **Login** - Authentication
- **Dashboard** - Project overview
- **ProjectView** - Scan list for a project
- **AnnotateView** - Label Studio integration
- **ReviewView** - 3D visualization and results
- **BatchSubmit** - Generate Kamiak job scripts
- **JobsView** - Track submitted jobs
- **AnalyticsView** - Charts and statistics

## Deployment

Deploy to Firebase Hosting:

```bash
npm run build
cd ../firebase
firebase deploy --only hosting
```

## Configuration

### Firebase
Update `.env` with your Firebase project credentials from the Firebase Console.

### API URL
Set `REACT_APP_API_URL` to your FastAPI backend URL (default: http://localhost:8000).

### Label Studio
Set `REACT_APP_LABEL_STUDIO_URL` to your Label Studio URL (default: http://localhost:8080).

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

### Adding New Features

1. Create new components in `src/components/`
2. Add new pages in `src/pages/`
3. Update routes in `App.js`
4. Add API endpoints in `src/api/client.js`

## Styling

This project uses Tailwind CSS for styling. See `tailwind.config.js` for configuration.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

