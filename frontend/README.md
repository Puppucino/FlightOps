# Flight Delay Prediction Dashboard - Frontend

React + TypeScript frontend for the intelligent flight delay prediction dashboard.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create environment file (optional):
```bash
# Create .env file if you need to override API URL
VITE_API_BASE_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and service functions
│   ├── components/    # React components (to be created)
│   ├── pages/         # Page components (to be created)
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Utility functions (to be created)
│   ├── App.tsx        # Main App component
│   └── main.tsx       # Application entry point
├── public/            # Static assets
├── package.json       # Dependencies and scripts
├── tsconfig.json      # TypeScript configuration
├── vite.config.ts     # Vite configuration
└── README.md          # This file
```

