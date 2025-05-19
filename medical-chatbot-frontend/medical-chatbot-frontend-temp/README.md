# Medical Chatbot Frontend

A simple React frontend for a medical chatbot application.

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the project directory
3. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

### Development

To start the development server:

```
npm start
```

The application will be available at [http://localhost:3000](http://localhost:3000).

### Build

To create a production build:

```
npm run build
```

The build files will be created in the `build` directory.

## Deployment to Azure

This project is configured for easy deployment to Azure Static Web Apps. When connected to a GitHub repository, it will automatically deploy whenever changes are pushed to the main branch.

1. Create an Azure Static Web App resource
2. Connect it to your GitHub repository
3. Configure the build settings:
   - Build Preset: React
   - App location: /
   - Output location: build

## Backend Integration

To connect this frontend to the backend:

1. Create a `.env` file in the root directory
2. Add the backend URL:
   ```
   REACT_APP_API_URL=https://your-backend-url
   ```
3. Update the API call in `App.js` to use the environment variable 