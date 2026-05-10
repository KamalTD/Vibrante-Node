# Vibrante-Node Website

## Setup

### 1. Install dependencies
```bash
cd website
npm install
```

### 2. Copy required assets

Before running the dev server, copy the following assets into the `public/` folder:

```bash
# From the project root (node_based_app/)
cp -r shots/ website/public/shots/
cp logo.png website/public/logo.png
cp splash.png website/public/splash.png

# Icons
mkdir -p website/public/icons
cp icons/houdini_icon.png website/public/icons/
cp icons/blender_icon.png website/public/icons/
cp icons/maya_icon.jpg website/public/icons/
cp icons/prism_icon.png website/public/icons/
cp icons/builder.png website/public/icons/
cp icons/vibrante-node-icon.png website/public/icons/

# SVG icons
cp icons/*.svg website/public/icons/

# Diagrams
mkdir -p website/public/diagrams
cp video_assets/maya_pipeline_3stages_diagram.svg website/public/diagrams/
cp video_assets/maya_headless_3stages.svg website/public/diagrams/
```

On Windows (PowerShell):
```powershell
# From the project root (node_based_app/)
Copy-Item -Recurse shots website\public\shots
Copy-Item logo.png website\public\logo.png
Copy-Item splash.png website\public\splash.png
Copy-Item -Recurse icons website\public\icons
New-Item -ItemType Directory -Force website\public\diagrams
Copy-Item video_assets\*.svg website\public\diagrams\
```

### 3. Run development server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### 4. Build for production
```bash
npm run build
npm start
```

## Structure

```
website/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout with SEO metadata
│   │   ├── page.tsx            # Homepage
│   │   ├── docs/page.tsx       # Documentation index
│   │   ├── showcase/page.tsx   # Workflow showcase
│   │   ├── developers/page.tsx # Developer experience
│   │   └── studio/page.tsx     # Studio/Enterprise page
│   └── components/
│       ├── layout/             # Navbar, Footer
│       ├── home/               # Homepage sections
│       ├── ui/                 # UI primitives
│       ├── showcase/           # Showcase components
│       └── developers/         # Developer page components
└── public/
    ├── shots/                  # App screenshots (copy from ../shots/)
    ├── icons/                  # App icons (copy from ../icons/)
    ├── diagrams/               # SVG diagrams (copy from ../video_assets/)
    ├── logo.png                # App logo (copy from ../)
    └── splash.png              # Splash screen (copy from ../)
```
