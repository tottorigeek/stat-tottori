<template>
  <div 
    ref="chartContainer" 
    class="d3-chart-container w-full h-full"
    :class="containerClass"
  >
    <div 
      ref="svgContainer" 
      class="svg-container w-full h-full"
    ></div>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'D3ChartBase',
  props: {
    data: {
      type: [Array, Object],
      default: () => []
    },
    width: {
      type: Number,
      default: 800
    },
    height: {
      type: Number,
      default: 600
    },
    containerClass: {
      type: String,
      default: ''
    },
    responsive: {
      type: Boolean,
      default: true
    }
  },
  emits: ['chart-initialized', 'chart-updated'],
  data() {
    return {
      svg: null,
      dimensions: {
        width: 0,
        height: 0
      },
      margin: {
        top: 20,
        right: 20,
        bottom: 30,
        left: 40
      }
    }
  },
  computed: {
    innerWidth() {
      return Math.max(0, this.dimensions.width - this.margin.left - this.margin.right)
    },
    innerHeight() {
      return Math.max(0, this.dimensions.height - this.margin.top - this.margin.bottom)
    }
  },
  mounted() {
    this.initializeChart()
    if (this.responsive) {
      this.setupResizeObserver()
    }
  },
  beforeUnmount() {
    this.cleanup()
  },
  watch: {
    data: {
      handler: 'updateChart',
      deep: true
    },
    width: 'updateDimensions',
    height: 'updateDimensions'
  },
  methods: {
    initializeChart() {
      this.updateDimensions()
      this.createSVG()
      this.drawChart()
      this.$emit('chart-initialized', this.svg)
    },

    updateDimensions() {
      if (this.responsive && this.$refs.chartContainer) {
        const rect = this.$refs.chartContainer.getBoundingClientRect()
        this.dimensions.width = rect.width || this.width
        this.dimensions.height = rect.height || this.height
      } else {
        this.dimensions.width = this.width
        this.dimensions.height = this.height
      }
    },

    createSVG() {
      if (this.svg) {
        this.svg.remove()
      }

      this.svg = d3.select(this.$refs.svgContainer)
        .append('svg')
        .attr('width', this.dimensions.width)
        .attr('height', this.dimensions.height)
        .attr('viewBox', `0 0 ${this.dimensions.width} ${this.dimensions.height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')

      // メイングループ
      this.g = this.svg.append('g')
        .attr('transform', `translate(${this.margin.left},${this.margin.top})`)
    },

    drawChart() {
      // サブクラスでオーバーライドする
      console.warn('drawChart method should be overridden in subclass')
    },

    updateChart() {
      if (this.svg) {
        this.drawChart()
        this.$emit('chart-updated', this.svg)
      }
    },

    setupResizeObserver() {
      if (typeof ResizeObserver !== 'undefined') {
        this.resizeObserver = new ResizeObserver(() => {
          this.handleResize()
        })
        this.resizeObserver.observe(this.$refs.chartContainer)
      } else {
        // フォールバック: window resize イベント
        window.addEventListener('resize', this.handleResize)
      }
    },

    handleResize() {
      clearTimeout(this.resizeTimer)
      this.resizeTimer = setTimeout(() => {
        this.updateDimensions()
        if (this.svg) {
          this.svg
            .attr('width', this.dimensions.width)
            .attr('height', this.dimensions.height)
            .attr('viewBox', `0 0 ${this.dimensions.width} ${this.dimensions.height}`)
          
          this.g.attr('transform', `translate(${this.margin.left},${this.margin.top})`)
          this.updateChart()
        }
      }, 100)
    },

    cleanup() {
      if (this.resizeObserver) {
        this.resizeObserver.disconnect()
      } else {
        window.removeEventListener('resize', this.handleResize)
      }
      if (this.resizeTimer) {
        clearTimeout(this.resizeTimer)
      }
      if (this.svg) {
        this.svg.remove()
      }
    },

    // D3ヘルパーメソッド
    createScale(type, domain, range) {
      const scaleTypes = {
        linear: d3.scaleLinear,
        ordinal: d3.scaleOrdinal,
        band: d3.scaleBand,
        time: d3.scaleTime,
        log: d3.scaleLog
      }
      
      const scale = scaleTypes[type]()
      if (domain) scale.domain(domain)
      if (range) scale.range(range)
      return scale
    },

    createAxis(scale, orientation = 'bottom') {
      const axisGenerators = {
        bottom: d3.axisBottom,
        top: d3.axisTop,
        left: d3.axisLeft,
        right: d3.axisRight
      }
      return axisGenerators[orientation](scale)
    },

    // アニメーション用ヘルパー
    transition(duration = 750) {
      return d3.transition().duration(duration)
    }
  }
}
</script>

<style scoped>
.d3-chart-container {
  position: relative;
}

.svg-container {
  overflow: visible;
}

:deep(svg) {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

:deep(.axis) {
  font-size: 12px;
}

:deep(.axis path),
:deep(.axis line) {
  fill: none;
  stroke: #6b7280;
  shape-rendering: crispEdges;
}

:deep(.axis text) {
  fill: #374151;
}

:deep(.grid line) {
  stroke: #e5e7eb;
  stroke-dasharray: 2,2;
}

:deep(.grid path) {
  stroke-width: 0;
}
</style>