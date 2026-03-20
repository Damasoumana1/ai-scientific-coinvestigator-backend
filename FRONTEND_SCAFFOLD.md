# Frontend Scaffold & Recommendations

## 🎨 Recommended Tech Stack

```
Next.js 14
├── React 18
├── TypeScript
├── Tailwind CSS
├── React Flow (for reasoning graphs)
└── Axios (API client)
```

---

## 📁 Suggested Project Structure

```
frontend/
├── public/
│   └── assets/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── upload/
│   │   │   └── page.tsx        # Paper upload
│   │   ├── analysis/
│   │   │   ├── page.tsx        # Analysis dashboard
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Analysis details
│   │   ├── protocols/
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Protocol view/edit
│   │   └── admin/
│   │       └── page.tsx        # Admin panel
│   ├── components/
│   │   ├── ui/                 # Reusable UI
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── layout/
│   │   ├── features/           # Feature components
│   │   │   ├── UploadZone.tsx
│   │   │   ├── ContradictionView.tsx
│   │   │   ├── ProtocolEditor.tsx
│   │   │   ├── ReasoningTracer.tsx
│   │   │   └── GraphVisualizer.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts       # Axios instance
│   │   │   ├── endpoints.ts    # API URLs
│   │   │   └── types.ts        # TypeScript interfaces
│   │   ├── hooks/
│   │   │   ├── useAnalysis.ts
│   │   │   ├── usePapers.ts
│   │   │   └── useProtocols.ts
│   │   └── utils/
│   │       ├── formatting.ts
│   │       └── validation.ts
│   ├── store/               # Zustand or Redux
│   │   ├── analysisStore.ts
│   │   └── userStore.ts
│   ├── styles/
│   │   └── globals.css     # Tailwind imports
│   └── types/
│       ├── analysis.ts
│       ├── protocol.ts
│       └── paper.ts
├── package.json
└── tsconfig.json
```

---

## 🚀 Getting Started

### 1. Create New Next.js Project
```bash
# Using create-next-app
npx create-next-app@latest scoinvestigator-frontend \
  --typescript \
  --tailwind \
  --eslint

cd scoinvestigator-frontend
```

### 2. Install Dependencies
```bash
npm install \
  axios \
  react-flow-renderer \
  zustand \
  react-icons \
  react-toastify

# Optional: for advanced visualizations
npm install \
  d3 \
  cytoscape \
  react-cytoscape
```

### 3. Environment Setup
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 🔑 Key Pages & Components

### 📄 Upload Papers (`/upload`)
```tsx
// Features:
- Drag & drop zone
- Multiple file upload
- PDF preview
- Progress indicator
- Metadata extraction preview

// Key component: UploadZone.tsx
```

### 📊 Analysis Dashboard (`/analysis`)
```tsx
// Features:
- List of all analyses
- Status indicators
- Timeline view
- Quick actions (view, export, delete)
- Filtering & search

// Key component: AnalysisList.tsx
```

### 🔍 Analysis Details (`/analysis/[id]`)
```tsx
// Features:
- Tabs: Summary | Contradictions | Hypotheses | Gaps | Protocols
- Reasoning trace visualization
- Metrics display
- Document references
- Export options

// Key components:
// - ContradictionView.tsx (table with severity scores)
// - ReasoningTracer.tsx (step-by-step breakdown)
// - GraphVisualizer.tsx (document relationships)
```

### 🧪 Protocol Designer (`/protocols/[id]`)
```tsx
// Features:
- Protocol editor (rich text or form)
- Variable specification
- Risk assessment form
- Cost/duration estimator
- Version history
- Export (PDF, DOCX, LaTeX)

// Key component: ProtocolEditor.tsx
```

### 📈 Reasoning Trace Visualization
```tsx
// Using React Flow:
Nodes: Analysis steps
Edges: Dependencies
Styling: Color-coded by status (pending/active/complete)
Interaction: Click to see details

// Key component: GraphVisualizer.tsx with react-flow-renderer
```

---

## 📡 API Integration

### API Client Setup
```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Main Endpoints to Integrate
```typescript
// lib/api/endpoints.ts
export const endpoints = {
  // Analysis
  analysis: {
    run: '/analysis/run',
    status: (id: string) => `/analysis/${id}/status`,
    results: (id: string) => `/analysis/${id}/results`,
  },
  // Papers
  papers: {
    upload: '/papers/upload',
    list: (projectId: string) => `/papers/${projectId}`,
  },
  // Protocols
  protocols: {
    generate: '/protocols/generate',
    list: '/protocols',
    detail: (id: string) => `/protocols/${id}`,
    export: (id: string, format: string) => `/protocols/${id}/export?format=${format}`,
  },
  // Health
  health: '/health/ready',
};
```

### Custom Hooks
```typescript
// lib/hooks/useAnalysis.ts
import { useState, useEffect } from 'react';
import apiClient from '@/lib/api/client';

export function useAnalysis(analysisId: string) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await apiClient.get(
          `/analysis/${analysisId}/results`
        );
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [analysisId]);

  return { data, loading, error };
}
```

---

## 🎨 UI Components (Tailwind)

### Theme & Colors
```tsx
// Suggested color scheme
Primary: Blue-600 (reasoning)
Secondary: Emerald-600 (validation)
Danger: Red-600 (contradictions)
Warning: Amber-600 (gaps)
```

### Key Components to Build

#### ContradictionCard
```tsx
interface Contradiction {
  id: string;
  variable: string;
  confidence: number;
  statement_a: string;
  statement_b: string;
  severity: 'low' | 'medium' | 'high';
}

<ContradictionCard 
  contradiction={contradiction}
  onResolve={handleResolve}
/>
```

#### HypothesisCard
```tsx
<HypothesisCard 
  hypothesis={hypothesis}
  stressTestResults={results}
  onSelect={handleSelect}
/>
```

#### ProtocolTimeline
```tsx
// Show: Hypothesis → Variables → Methodology → Risk Analysis → Export
<ProtocolTimeline steps={protocolSteps} />
```

---

## 📊 Graph Visualization (React Flow)

### Reasoning Trace Graph
```typescript
// components/features/ReasoningTracer.tsx
import { useCallback } from 'react';
import ReactFlow, { 
  Node, 
  Edge, 
  useNodesState, 
  useEdgesState 
} from 'reactflow';

const nodes: Node[] = [
  { id: '1', data: { label: 'Extract Documents' }, position: { x: 0, y: 0 } },
  { id: '2', data: { label: 'Detect Contradictions' }, position: { x: 250, y: 0 } },
  // ... more nodes
];

const edges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
  // ... more edges
];
```

---

## 🔐 Authentication

### Token Management
```typescript
// lib/api/auth.ts
export const auth = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', { email, password });
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  },
  getToken: () => localStorage.getItem('token'),
};
```

---

## 📦 Deployment Options

### Vercel (Recommended)
```bash
# Connect GitHub repo to Vercel
# Auto-deploys on push
# Environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://api.railway.app/api/v1
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 🚨 Error Handling

```typescript
// Global error boundary
// components/layout/ErrorBoundary.tsx
import { ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

export default function ErrorBoundary({ children }: Props) {
  try {
    return <>{children}</>;
  } catch (error) {
    return (
      <div className="bg-red-50 p-4 rounded">
        <h2>Something went wrong</h2>
        <p>{error.message}</p>
      </div>
    );
  }
}
```

---

## 📱 Responsive Design

Use Tailwind breakpoints:
```tsx
// Mobile first
className="w-full md:w-1/2 lg:w-1/3"

// Responsive grid
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
```

---

## 🧪 Testing

```bash
# Install testing dependencies
npm install --save-dev @testing-library/react jest

# Example test
// __tests__/components/ContradictionCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ContradictionCard } from '@/components/features/ContradictionCard';

describe('ContradictionCard', () => {
  it('renders contradiction data', () => {
    const contradiction = {
      variable: 'sample_size',
      confidence: 0.95,
    };
    render(<ContradictionCard contradiction={contradiction} />);
    expect(screen.getByText('sample_size')).toBeInTheDocument();
  });
});
```

---

## 📝 Quick Development Checklist

- [ ] Setup Next.js project
- [ ] Configure API client & endpoints
- [ ] Create layout components (Header, Sidebar)
- [ ] Implement upload page
- [ ] Build analysis dashboard
- [ ] Create analysis detail pages
- [ ] Add protocol editor
- [ ] Implement reasoning trace visualization
- [ ] Setup authentication flow
- [ ] Add error handling & loading states
- [ ] Global styling with Tailwind
- [ ] Responsive design testing
- [ ] Performance optimization
- [ ] Deploy to Vercel

---

## 🎯 UX/Design Tips for Jury

**Scientific credibility:**
- Show data sources and references
- Display confidence scores
- Allow result verification
- Show reasoning steps

**Visual hierarchy:**
- Emphasize contradictions clearly
- Highlight key hypotheses
- Color-code severity/confidence
- Use data visualization effectively

**Performance:**
- Quick upload/processing feedback
- Real-time progress indicators
- Smooth transitions
- Responsive to all devices

---

## 📚 Resources

- [Next.js Docs](https://nextjs.org/docs)
- [React Flow](https://reactflow.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [TypeScript](https://www.typescriptlang.org/)
- [Axios](https://axios-http.com/)

---

Happy building! 🚀
