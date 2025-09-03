<template>
  <div class="network-visualization">
    <div class="controls mb-4 flex flex-wrap gap-4">
      <div class="flex items-center">
        <label class="mr-2 text-sm font-medium text-gray-700">Force強度:</label>
        <input
          v-model.number="forceStrength"
          type="range"
          min="0"
          max="100"
          class="range range-sm"
          @input="updateForces"
        />
        <span class="ml-2 text-sm text-gray-600">{{ forceStrength }}%</span>
      </div>
      
      <div class="flex items-center">
        <label class="mr-2 text-sm font-medium text-gray-700">接続距離:</label>
        <input
          v-model.number="linkDistance"
          type="range"
          min="10"
          max="200"
          class="range range-sm"
          @input="updateForces"
        />
        <span class="ml-2 text-sm text-gray-600">{{ linkDistance }}px</span>
      </div>

      <button
        @click="restartSimulation"
        class="btn btn-sm btn-primary"
      >
        シミュレーション再開
      </button>

      <button
        @click="centerGraph"
        class="btn btn-sm btn-secondary"
      >
        中央揃え
      </button>
    </div>

    <D3ChartBase
      ref="chart"
      :data="networkData"
      :height="height"
      :width="width"
      :responsive="responsive"
      container-class="border border-gray-200 rounded-lg"
      @chart-initialized="onChartInitialized"
      @chart-updated="onChartUpdated"
    />

    <!-- ツールチップ -->
    <div
      ref="tooltip"
      class="absolute opacity-0 bg-gray-800 text-white px-3 py-2 rounded-lg text-sm pointer-events-none z-10 transition-opacity duration-200"
      style="transform: translateX(-50%) translateY(-100%)"
    >
      <div class="tooltip-content"></div>
    </div>

    <!-- レジェンド -->
    <div class="legend mt-4">
      <h4 class="text-sm font-semibold text-gray-700 mb-2">凡例</h4>
      <div class="flex flex-wrap gap-4">
        <div
          v-for="category in nodeCategories"
          :key="category.key"
          class="flex items-center"
        >
          <div
            class="w-4 h-4 rounded-full mr-2"
            :style="{ backgroundColor: category.color }"
          ></div>
          <span class="text-sm text-gray-600">{{ category.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import D3ChartBase from './D3ChartBase.vue'

export default {
  name: 'NetworkVisualization',
  components: {
    D3ChartBase
  },
  props: {
    nodes: {
      type: Array,
      default: () => []
    },
    links: {
      type: Array,
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
    responsive: {
      type: Boolean,
      default: true
    },
    categoryField: {
      type: String,
      default: 'category'
    },
    labelField: {
      type: String,
      default: 'name'
    },
    valueField: {
      type: String,
      default: 'value'
    }
  },
  emits: ['node-click', 'node-hover', 'link-click'],
  data() {
    return {
      simulation: null,
      forceStrength: 30,
      linkDistance: 50,
      colorScale: null,
      nodeCategories: [],
      tooltip: null
    }
  },
  computed: {
    networkData() {
      return {
        nodes: this.nodes.map(d => ({ ...d })),
        links: this.links.map(d => ({ ...d }))
      }
    }
  },
  watch: {
    networkData: {
      handler: 'updateVisualization',
      deep: true
    }
  },
  methods: {
    onChartInitialized(svg) {
      this.svg = svg
      this.setupColorScale()
      this.createSimulation()
      this.drawNetwork()
    },

    onChartUpdated() {
      this.updateVisualization()
    },

    setupColorScale() {
      const categories = [...new Set(this.nodes.map(d => d[this.categoryField]))]
      this.colorScale = d3.scaleOrdinal(d3.schemeCategory10)
        .domain(categories)
      
      this.nodeCategories = categories.map(cat => ({
        key: cat,
        label: cat,
        color: this.colorScale(cat)
      }))
    },

    createSimulation() {
      const chart = this.$refs.chart

      this.simulation = d3.forceSimulation(this.networkData.nodes)
        .force('link', d3.forceLink(this.networkData.links)
          .id(d => d.id)
          .distance(this.linkDistance)
        )
        .force('charge', d3.forceManyBody().strength(-this.forceStrength * 3))
        .force('center', d3.forceCenter(chart.innerWidth / 2, chart.innerHeight / 2))
        .force('collision', d3.forceCollide().radius(d => this.getNodeRadius(d) + 2))
    },

    drawNetwork() {
      if (!this.svg || !this.networkData) return

      const chart = this.$refs.chart
      
      // リンクの描画
      this.linkSelection = chart.g.selectAll('.link')
        .data(this.networkData.links, d => `${d.source.id}-${d.target.id}`)
      
      this.linkSelection.exit().remove()
      
      const linkEnter = this.linkSelection.enter()
        .append('line')
        .attr('class', 'link')
        .style('stroke', '#999')
        .style('stroke-opacity', 0.6)
        .style('stroke-width', d => Math.sqrt(d.value || 1) * 2)
        .style('cursor', 'pointer')
        .on('click', (event, d) => {
          this.$emit('link-click', d, event)
        })

      this.linkSelection = linkEnter.merge(this.linkSelection)

      // ノードの描画
      this.nodeSelection = chart.g.selectAll('.node')
        .data(this.networkData.nodes, d => d.id)
      
      this.nodeSelection.exit().remove()
      
      const nodeEnter = this.nodeSelection.enter()
        .append('g')
        .attr('class', 'node')
        .style('cursor', 'pointer')
        .call(this.createDragBehavior())
        .on('click', (event, d) => {
          this.$emit('node-click', d, event)
        })
        .on('mouseover', (event, d) => {
          this.showTooltip(event, d)
          this.$emit('node-hover', d, event)
        })
        .on('mouseout', () => {
          this.hideTooltip()
        })

      // ノードの円
      nodeEnter.append('circle')
        .attr('r', d => this.getNodeRadius(d))
        .style('fill', d => this.colorScale(d[this.categoryField]))
        .style('stroke', '#fff')
        .style('stroke-width', 2)

      // ノードのラベル
      nodeEnter.append('text')
        .attr('dy', '.35em')
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('fill', '#333')
        .style('pointer-events', 'none')
        .text(d => d[this.labelField])

      this.nodeSelection = nodeEnter.merge(this.nodeSelection)

      // シミュレーション更新の設定
      this.simulation.on('tick', () => {
        this.linkSelection
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y)

        this.nodeSelection
          .attr('transform', d => `translate(${d.x},${d.y})`)
      })
    },

    getNodeRadius(node) {
      const baseRadius = 8
      const value = node[this.valueField] || 1
      return baseRadius + Math.sqrt(value) * 2
    },

    createDragBehavior() {
      return d3.drag()
        .on('start', (event, d) => {
          if (!event.active) this.simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on('drag', (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on('end', (event, d) => {
          if (!event.active) this.simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        })
    },

    updateForces() {
      if (this.simulation) {
        this.simulation
          .force('charge', d3.forceManyBody().strength(-this.forceStrength * 3))
          .force('link', d3.forceLink(this.networkData.links)
            .id(d => d.id)
            .distance(this.linkDistance)
          )
          .alpha(1)
          .restart()
      }
    },

    restartSimulation() {
      if (this.simulation) {
        this.simulation.alpha(1).restart()
      }
    },

    centerGraph() {
      const chart = this.$refs.chart
      if (this.simulation && chart) {
        this.simulation
          .force('center', d3.forceCenter(chart.innerWidth / 2, chart.innerHeight / 2))
          .alpha(1)
          .restart()
      }
    },

    updateVisualization() {
      if (this.svg) {
        this.setupColorScale()
        this.createSimulation()
        this.drawNetwork()
      }
    },

    showTooltip(event, node) {
      const tooltip = this.$refs.tooltip
      const content = tooltip.querySelector('.tooltip-content')
      
      content.innerHTML = `
        <div class="font-semibold">${node[this.labelField]}</div>
        <div>カテゴリ: ${node[this.categoryField]}</div>
        <div>値: ${node[this.valueField] || 'N/A'}</div>
      `

      tooltip.style.left = event.pageX + 'px'
      tooltip.style.top = event.pageY + 'px'
      tooltip.style.opacity = '1'
    },

    hideTooltip() {
      const tooltip = this.$refs.tooltip
      tooltip.style.opacity = '0'
    }
  },

  beforeUnmount() {
    if (this.simulation) {
      this.simulation.stop()
    }
  }
}
</script>

<style scoped>
.range {
  @apply w-24;
}

.btn {
  @apply px-3 py-1 rounded text-sm font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-500 text-white hover:bg-blue-600;
}

.btn-secondary {
  @apply bg-gray-500 text-white hover:bg-gray-600;
}

.btn-sm {
  @apply px-2 py-1 text-xs;
}

:deep(.node circle:hover) {
  stroke-width: 3px;
}

:deep(.link:hover) {
  stroke-opacity: 1 !important;
  stroke-width: 4px !important;
}
</style>