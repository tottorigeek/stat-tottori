<template>
  <div class="time-series-analysis">
    <div class="controls mb-4 flex flex-wrap gap-4 items-center">
      <div class="flex items-center">
        <label class="mr-2 text-sm font-medium text-gray-700">表示系列:</label>
        <div class="flex flex-wrap gap-2">
          <label
            v-for="series in availableSeries"
            :key="series.key"
            class="flex items-center"
          >
            <input
              v-model="visibleSeries"
              :value="series.key"
              type="checkbox"
              class="mr-1"
            />
            <span
              class="text-sm px-2 py-1 rounded"
              :style="{ backgroundColor: series.color, color: '#fff' }"
            >
              {{ series.label }}
            </span>
          </label>
        </div>
      </div>

      <button
        @click="resetZoom"
        class="btn btn-sm btn-secondary"
      >
        ズームリセット
      </button>

      <div class="flex items-center">
        <label class="mr-2 text-sm font-medium text-gray-700">アニメーション:</label>
        <input
          v-model="enableAnimation"
          type="checkbox"
          class="checkbox"
        />
      </div>
    </div>

    <D3ChartBase
      ref="chart"
      :data="timeSeriesData"
      :height="height"
      :width="width"
      :responsive="responsive"
      container-class="border border-gray-200 rounded-lg bg-white"
      @chart-initialized="onChartInitialized"
      @chart-updated="onChartUpdated"
    />

    <!-- ブラシ選択エリア -->
    <div
      v-if="showBrush"
      class="brush-context mt-4"
    >
      <D3ChartBase
        ref="brushChart"
        :data="timeSeriesData"
        :height="80"
        :width="width"
        :responsive="responsive"
        container-class="border border-gray-200 rounded bg-gray-50"
        @chart-initialized="onBrushChartInitialized"
      />
    </div>

    <!-- 選択された期間の情報表示 -->
    <div
      v-if="selectedPeriod.start && selectedPeriod.end"
      class="selected-period mt-4 p-3 bg-blue-50 rounded-lg"
    >
      <h4 class="text-sm font-semibold text-blue-800 mb-2">選択期間の統計</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div
          v-for="stat in periodStats"
          :key="stat.label"
          class="text-center"
        >
          <div class="text-gray-600">{{ stat.label }}</div>
          <div class="font-medium text-gray-900">{{ stat.value }}</div>
        </div>
      </div>
    </div>

    <!-- ツールチップ -->
    <div
      ref="tooltip"
      class="absolute opacity-0 bg-gray-800 text-white px-3 py-2 rounded-lg text-sm pointer-events-none z-10 transition-opacity duration-200"
    >
      <div class="tooltip-content"></div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import D3ChartBase from './D3ChartBase.vue'

export default {
  name: 'TimeSeriesAnalysis',
  components: {
    D3ChartBase
  },
  props: {
    data: {
      type: Array,
      default: () => []
    },
    width: {
      type: Number,
      default: 800
    },
    height: {
      type: Number,
      default: 400
    },
    responsive: {
      type: Boolean,
      default: true
    },
    dateField: {
      type: String,
      default: 'date'
    },
    valueFields: {
      type: Array,
      default: () => ['value']
    },
    showBrush: {
      type: Boolean,
      default: true
    },
    enableZoom: {
      type: Boolean,
      default: true
    }
  },
  emits: ['period-selected', 'data-hover'],
  data() {
    return {
      xScale: null,
      yScale: null,
      line: null,
      area: null,
      zoom: null,
      brush: null,
      visibleSeries: [],
      enableAnimation: true,
      selectedPeriod: {
        start: null,
        end: null
      },
      availableSeries: [],
      colorScale: null
    }
  },
  computed: {
    timeSeriesData() {
      if (!this.data || this.data.length === 0) return []
      
      return this.data.map(d => ({
        ...d,
        [this.dateField]: new Date(d[this.dateField])
      })).sort((a, b) => a[this.dateField] - b[this.dateField])
    },

    periodStats() {
      if (!this.selectedPeriod.start || !this.selectedPeriod.end) return []
      
      const filtered = this.timeSeriesData.filter(d => 
        d[this.dateField] >= this.selectedPeriod.start && 
        d[this.dateField] <= this.selectedPeriod.end
      )

      const stats = []
      this.visibleSeries.forEach(seriesKey => {
        const values = filtered.map(d => d[seriesKey]).filter(v => v != null)
        if (values.length > 0) {
          const avg = d3.mean(values)
          const min = d3.min(values)
          const max = d3.max(values)
          
          stats.push(
            { label: `${seriesKey} 平均`, value: this.formatValue(avg) },
            { label: `${seriesKey} 最小`, value: this.formatValue(min) },
            { label: `${seriesKey} 最大`, value: this.formatValue(max) }
          )
        }
      })
      
      return stats
    }
  },
  watch: {
    timeSeriesData: {
      handler: 'updateVisualization',
      deep: true
    },
    visibleSeries: 'updateVisualization',
    enableAnimation: 'updateVisualization'
  },
  mounted() {
    this.initializeSeriesConfig()
  },
  methods: {
    initializeSeriesConfig() {
      this.colorScale = d3.scaleOrdinal(d3.schemeCategory10)
      
      this.availableSeries = this.valueFields.map(field => ({
        key: field,
        label: field,
        color: this.colorScale(field)
      }))
      
      this.visibleSeries = [...this.valueFields]
    },

    onChartInitialized(svg) {
      this.svg = svg
      this.setupScales()
      this.setupZoom()
      this.drawChart()
    },

    onChartUpdated() {
      this.updateVisualization()
    },

    onBrushChartInitialized(svg) {
      this.brushSvg = svg
      this.setupBrush()
      this.drawBrushChart()
    },

    setupScales() {
      const chart = this.$refs.chart
      const data = this.timeSeriesData

      if (data.length === 0) return

      this.xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d[this.dateField]))
        .range([0, chart.innerWidth])

      const allValues = []
      this.visibleSeries.forEach(series => {
        data.forEach(d => {
          if (d[series] != null) allValues.push(d[series])
        })
      })

      this.yScale = d3.scaleLinear()
        .domain(d3.extent(allValues))
        .nice()
        .range([chart.innerHeight, 0])
    },

    setupZoom() {
      if (!this.enableZoom) return

      const chart = this.$refs.chart

      this.zoom = d3.zoom()
        .scaleExtent([1, 10])
        .extent([[0, 0], [chart.innerWidth, chart.innerHeight]])
        .on('zoom', (event) => {
          const transform = event.transform
          const newXScale = transform.rescaleX(this.xScale)
          
          this.updateAxes(newXScale, this.yScale)
          this.updateLines(newXScale, this.yScale)
        })

      chart.svg.call(this.zoom)
    },

    setupBrush() {
      if (!this.showBrush) return

      const brushChart = this.$refs.brushChart

      this.brush = d3.brushX()
        .extent([[0, 0], [brushChart.innerWidth, brushChart.innerHeight]])
        .on('brush end', (event) => {
          if (event.selection) {
            const [x0, x1] = event.selection.map(this.xScale.invert)
            this.selectedPeriod.start = x0
            this.selectedPeriod.end = x1
            this.$emit('period-selected', { start: x0, end: x1 })
          }
        })

      brushChart.g.append('g')
        .attr('class', 'brush')
        .call(this.brush)
    },

    drawChart() {
      if (!this.svg || this.timeSeriesData.length === 0) return

      const chart = this.$refs.chart
      
      // 軸の描画
      this.drawAxes()
      
      // グリッドの描画
      this.drawGrid()
      
      // ラインの描画
      this.drawLines()
      
      // インタラクション要素の追加
      this.addInteractions()
    },

    drawAxes() {
      const chart = this.$refs.chart

      // X軸
      const xAxis = d3.axisBottom(this.xScale)
        .tickFormat(d3.timeFormat('%Y/%m'))
        .ticks(6)

      chart.g.selectAll('.x-axis').remove()
      chart.g.append('g')
        .attr('class', 'x-axis axis')
        .attr('transform', `translate(0,${chart.innerHeight})`)
        .call(xAxis)

      // Y軸
      const yAxis = d3.axisLeft(this.yScale)
        .ticks(6)
        .tickFormat(d => this.formatValue(d))

      chart.g.selectAll('.y-axis').remove()
      chart.g.append('g')
        .attr('class', 'y-axis axis')
        .call(yAxis)

      // 軸ラベル
      chart.g.selectAll('.axis-label').remove()
      chart.g.append('text')
        .attr('class', 'axis-label')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0 - chart.margin.left)
        .attr('x', 0 - (chart.innerHeight / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('fill', '#666')
        .text('値')
    },

    drawGrid() {
      const chart = this.$refs.chart

      // Y軸グリッド
      chart.g.selectAll('.grid').remove()
      chart.g.append('g')
        .attr('class', 'grid')
        .call(d3.axisLeft(this.yScale)
          .tickSize(-chart.innerWidth)
          .tickFormat('')
        )
    },

    drawLines() {
      const chart = this.$refs.chart
      
      this.line = d3.line()
        .x(d => this.xScale(d[this.dateField]))
        .y((d, i, arr) => this.yScale(d[arr.seriesKey]))
        .curve(d3.curveMonotoneX)

      chart.g.selectAll('.line-group').remove()
      
      this.visibleSeries.forEach(seriesKey => {
        const seriesData = this.timeSeriesData.filter(d => d[seriesKey] != null)
        seriesData.seriesKey = seriesKey

        const lineGroup = chart.g.append('g')
          .attr('class', 'line-group')
          .datum(seriesData)

        // ライン
        lineGroup.append('path')
          .attr('class', 'line')
          .attr('d', this.line)
          .style('fill', 'none')
          .style('stroke', this.colorScale(seriesKey))
          .style('stroke-width', 2)
          .style('opacity', 0.8)

        if (this.enableAnimation) {
          lineGroup.select('.line')
            .attr('stroke-dasharray', function() {
              return this.getTotalLength() + ' ' + this.getTotalLength()
            })
            .attr('stroke-dashoffset', function() {
              return this.getTotalLength()
            })
            .transition()
            .duration(2000)
            .attr('stroke-dashoffset', 0)
        }

        // データポイント
        lineGroup.selectAll('.dot')
          .data(seriesData)
          .enter().append('circle')
          .attr('class', 'dot')
          .attr('cx', d => this.xScale(d[this.dateField]))
          .attr('cy', d => this.yScale(d[seriesKey]))
          .attr('r', 3)
          .style('fill', this.colorScale(seriesKey))
          .style('opacity', 0.8)
          .on('mouseover', (event, d) => {
            this.showTooltip(event, d, seriesKey)
          })
          .on('mouseout', this.hideTooltip)
      })
    },

    drawBrushChart() {
      if (!this.brushSvg || !this.showBrush) return

      const brushChart = this.$refs.brushChart
      const data = this.timeSeriesData

      const brushXScale = d3.scaleTime()
        .domain(d3.extent(data, d => d[this.dateField]))
        .range([0, brushChart.innerWidth])

      const allValues = []
      this.visibleSeries.forEach(series => {
        data.forEach(d => {
          if (d[series] != null) allValues.push(d[series])
        })
      })

      const brushYScale = d3.scaleLinear()
        .domain(d3.extent(allValues))
        .range([brushChart.innerHeight, 0])

      const brushLine = d3.line()
        .x(d => brushXScale(d[this.dateField]))
        .y((d, i, arr) => brushYScale(d[arr.seriesKey]))
        .curve(d3.curveMonotoneX)

      this.visibleSeries.forEach(seriesKey => {
        const seriesData = this.timeSeriesData.filter(d => d[seriesKey] != null)
        seriesData.seriesKey = seriesKey

        brushChart.g.append('path')
          .datum(seriesData)
          .attr('class', 'brush-line')
          .attr('d', brushLine)
          .style('fill', 'none')
          .style('stroke', this.colorScale(seriesKey))
          .style('stroke-width', 1)
          .style('opacity', 0.6)
      })
    },

    updateAxes(xScale, yScale) {
      const chart = this.$refs.chart

      const xAxis = d3.axisBottom(xScale)
        .tickFormat(d3.timeFormat('%Y/%m'))
        .ticks(6)

      chart.g.select('.x-axis')
        .transition()
        .duration(this.enableAnimation ? 300 : 0)
        .call(xAxis)
    },

    updateLines(xScale, yScale) {
      const chart = this.$refs.chart

      const line = d3.line()
        .x(d => xScale(d[this.dateField]))
        .y((d, i, arr) => yScale(d[arr.seriesKey]))
        .curve(d3.curveMonotoneX)

      chart.g.selectAll('.line')
        .transition()
        .duration(this.enableAnimation ? 300 : 0)
        .attr('d', line)

      chart.g.selectAll('.dot')
        .transition()
        .duration(this.enableAnimation ? 300 : 0)
        .attr('cx', d => xScale(d[this.dateField]))
        .attr('cy', (d, i, nodes) => {
          const seriesKey = d3.select(nodes[i].parentNode).datum().seriesKey
          return yScale(d[seriesKey])
        })
    },

    addInteractions() {
      const chart = this.$refs.chart

      // ホバーライン
      const hoverLine = chart.g.append('line')
        .attr('class', 'hover-line')
        .style('stroke', '#666')
        .style('stroke-width', 1)
        .style('stroke-dasharray', '3,3')
        .style('opacity', 0)
        .attr('y1', 0)
        .attr('y2', chart.innerHeight)

      // マウストラッキング
      chart.g.append('rect')
        .attr('class', 'mouse-tracker')
        .attr('width', chart.innerWidth)
        .attr('height', chart.innerHeight)
        .style('fill', 'none')
        .style('pointer-events', 'all')
        .on('mousemove', (event) => {
          const [mouseX] = d3.pointer(event)
          const date = this.xScale.invert(mouseX)
          
          hoverLine
            .style('opacity', 1)
            .attr('x1', mouseX)
            .attr('x2', mouseX)

          this.showInteractionTooltip(event, date)
        })
        .on('mouseleave', () => {
          hoverLine.style('opacity', 0)
          this.hideTooltip()
        })
    },

    updateVisualization() {
      if (this.svg) {
        this.setupScales()
        this.drawChart()
      }
      if (this.brushSvg && this.showBrush) {
        this.drawBrushChart()
      }
    },

    resetZoom() {
      if (this.zoom && this.svg) {
        const chart = this.$refs.chart
        chart.svg.transition().duration(750).call(
          this.zoom.transform,
          d3.zoomIdentity
        )
      }
    },

    showTooltip(event, data, seriesKey) {
      const tooltip = this.$refs.tooltip
      const content = tooltip.querySelector('.tooltip-content')
      
      content.innerHTML = `
        <div class="font-semibold">${d3.timeFormat('%Y/%m/%d')(data[this.dateField])}</div>
        <div style="color: ${this.colorScale(seriesKey)}">${seriesKey}: ${this.formatValue(data[seriesKey])}</div>
      `

      tooltip.style.left = event.pageX + 10 + 'px'
      tooltip.style.top = event.pageY - 10 + 'px'
      tooltip.style.opacity = '1'
    },

    showInteractionTooltip(event, date) {
      const tooltip = this.$refs.tooltip
      const content = tooltip.querySelector('.tooltip-content')
      
      // 最も近いデータポイントを見つける
      const bisect = d3.bisector(d => d[this.dateField]).left
      const index = bisect(this.timeSeriesData, date, 1)
      const d0 = this.timeSeriesData[index - 1]
      const d1 = this.timeSeriesData[index]
      const d = (d1 && (date - d0[this.dateField] > d1[this.dateField] - date)) ? d1 : d0

      if (d) {
        let html = `<div class="font-semibold">${d3.timeFormat('%Y/%m/%d')(d[this.dateField])}</div>`
        
        this.visibleSeries.forEach(seriesKey => {
          if (d[seriesKey] != null) {
            html += `<div style="color: ${this.colorScale(seriesKey)}">${seriesKey}: ${this.formatValue(d[seriesKey])}</div>`
          }
        })
        
        content.innerHTML = html

        tooltip.style.left = event.pageX + 10 + 'px'
        tooltip.style.top = event.pageY - 10 + 'px'
        tooltip.style.opacity = '1'
      }
    },

    hideTooltip() {
      this.$refs.tooltip.style.opacity = '0'
    },

    formatValue(value) {
      if (value == null) return 'N/A'
      return d3.format(',.1f')(value)
    }
  }
}
</script>

<style scoped>
.checkbox {
  @apply w-4 h-4;
}

.btn {
  @apply px-3 py-1 rounded text-sm font-medium transition-colors;
}

.btn-secondary {
  @apply bg-gray-500 text-white hover:bg-gray-600;
}

.btn-sm {
  @apply px-2 py-1 text-xs;
}

:deep(.line:hover) {
  stroke-width: 3px !important;
}

:deep(.dot:hover) {
  r: 5px !important;
  stroke: #333 !important;
  stroke-width: 2px !important;
}

:deep(.brush .selection) {
  stroke: #666;
  fill: rgba(102, 102, 102, 0.2);
}
</style>