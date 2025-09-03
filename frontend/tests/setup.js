// Vitest テストセットアップファイル
import { vi } from 'vitest'

// Chart.js のモック
vi.mock('chart.js', () => ({
  Chart: {
    register: vi.fn(),
    defaults: {
      font: {
        family: 'sans-serif'
      }
    }
  },
  CategoryScale: vi.fn(),
  LinearScale: vi.fn(),
  PointElement: vi.fn(),
  LineElement: vi.fn(),
  Title: vi.fn(),
  Tooltip: vi.fn(),
  Legend: vi.fn(),
  ArcElement: vi.fn(),
  BarElement: vi.fn(),
  registerables: [
    vi.fn(), // CategoryScale
    vi.fn(), // LinearScale
    vi.fn(), // PointElement
    vi.fn(), // LineElement
    vi.fn(), // Title
    vi.fn(), // Tooltip
    vi.fn(), // Legend
    vi.fn(), // ArcElement
    vi.fn()  // BarElement
  ]
}))

// vue-chartjs のモック
vi.mock('vue-chartjs', () => ({
  Line: {
    name: 'Line',
    template: '<div data-testid="chart-line">Line Chart</div>'
  },
  Bar: {
    name: 'Bar', 
    template: '<div data-testid="chart-bar">Bar Chart</div>'
  },
  Pie: {
    name: 'Pie',
    template: '<div data-testid="chart-pie">Pie Chart</div>'
  },
  Radar: {
    name: 'Radar',
    template: '<div data-testid="chart-radar">Radar Chart</div>'
  }
}))

// Mapbox GL のモック
vi.mock('mapbox-gl', () => ({
  Map: vi.fn(() => ({
    on: vi.fn(),
    addControl: vi.fn(),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    setLayoutProperty: vi.fn(),
    remove: vi.fn()
  })),
  NavigationControl: vi.fn(),
  GeolocateControl: vi.fn(),
  Marker: vi.fn(() => ({
    setLngLat: vi.fn(() => ({ addTo: vi.fn() }))
  }))
}))

// D3.js のモック
vi.mock('d3', () => ({
  select: vi.fn(() => ({
    append: vi.fn(() => ({
      attr: vi.fn().mockReturnThis(),
      style: vi.fn().mockReturnThis(),
      text: vi.fn().mockReturnThis(),
      selectAll: vi.fn().mockReturnThis()
    })),
    selectAll: vi.fn().mockReturnThis(),
    attr: vi.fn().mockReturnThis(),
    style: vi.fn().mockReturnThis()
  })),
  scaleLinear: vi.fn(() => ({
    domain: vi.fn().mockReturnThis(),
    range: vi.fn().mockReturnThis(),
    nice: vi.fn().mockReturnThis()
  })),
  scaleTime: vi.fn(() => ({
    domain: vi.fn().mockReturnThis(),
    range: vi.fn().mockReturnThis()
  })),
  scaleOrdinal: vi.fn(() => ({
    domain: vi.fn().mockReturnThis(),
    range: vi.fn().mockReturnThis()
  })),
  schemeCategory10: ['#1f77b4', '#ff7f0e', '#2ca02c'],
  line: vi.fn(() => ({
    x: vi.fn().mockReturnThis(),
    y: vi.fn().mockReturnThis(),
    curve: vi.fn().mockReturnThis()
  })),
  axisBottom: vi.fn(),
  axisLeft: vi.fn(),
  extent: vi.fn(() => [0, 100]),
  max: vi.fn(() => 100),
  min: vi.fn(() => 0),
  mean: vi.fn(() => 50),
  format: vi.fn(() => vi.fn()),
  timeFormat: vi.fn(() => vi.fn()),
  forceSimulation: vi.fn(() => ({
    force: vi.fn().mockReturnThis(),
    on: vi.fn().mockReturnThis(),
    alpha: vi.fn().mockReturnThis(),
    alphaTarget: vi.fn().mockReturnThis(),
    restart: vi.fn().mockReturnThis(),
    stop: vi.fn()
  })),
  forceLink: vi.fn(),
  forceManyBody: vi.fn(() => ({
    strength: vi.fn().mockReturnThis()
  })),
  forceCenter: vi.fn(),
  forceCollide: vi.fn(() => ({
    radius: vi.fn().mockReturnThis()
  })),
  drag: vi.fn(() => ({
    on: vi.fn().mockReturnThis()
  })),
  zoom: vi.fn(() => ({
    scaleExtent: vi.fn().mockReturnThis(),
    extent: vi.fn().mockReturnThis(),
    on: vi.fn().mockReturnThis()
  })),
  brushX: vi.fn(() => ({
    extent: vi.fn().mockReturnThis(),
    on: vi.fn().mockReturnThis()
  })),
  transition: vi.fn(() => ({
    duration: vi.fn().mockReturnThis()
  })),
  pointer: vi.fn(() => [0, 0]),
  bisector: vi.fn(() => ({
    left: vi.fn(() => 0)
  })),
  curveMonotoneX: 'curveMonotoneX'
}))

// Canvas API のモック
global.HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
  fillRect: vi.fn(),
  clearRect: vi.fn(),
  getImageData: vi.fn(() => ({ data: new Array(4) })),
  putImageData: vi.fn(),
  createImageData: vi.fn(() => ({ data: new Array(4) })),
  setTransform: vi.fn(),
  drawImage: vi.fn(),
  save: vi.fn(),
  restore: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  closePath: vi.fn(),
  stroke: vi.fn(),
  fill: vi.fn(),
  measureText: vi.fn(() => ({ width: 0 })),
  arc: vi.fn(),
  fillText: vi.fn()
}))

global.HTMLCanvasElement.prototype.toDataURL = vi.fn(() => 'data:image/png;base64,test')

// ResizeObserver のモック
global.ResizeObserver = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// console.warn を抑制（開発時の警告）
const originalWarn = console.warn
beforeAll(() => {
  console.warn = vi.fn()
})

afterAll(() => {
  console.warn = originalWarn
})