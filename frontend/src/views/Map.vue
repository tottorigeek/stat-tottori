<template>
  <div class="map-container">
    <!-- ナビゲーションバー -->
    <nav class="map-nav bg-white shadow-lg z-50 relative">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-6">
            <router-link to="/" class="text-blue-600 hover:text-blue-800 font-semibold">
              🏔️ すたっととっとり
            </router-link>
            <div class="text-sm text-gray-600">統計データ3D地図</div>
          </div>
          <div class="flex items-center space-x-4">
            <select v-model="selectedDataType" @change="updateMapData" class="text-sm border rounded px-3 py-1">
              <option value="population">人口密度</option>
              <option value="age">高齢化率</option>
              <option value="income">平均所得</option>
              <option value="employment">就業率</option>
              <option value="healthcare">医療施設密度</option>
              <option value="education">教育施設密度</option>
            </select>
            <select v-model="selectedVisualization" @change="updateVisualization" class="text-sm border rounded px-3 py-1">
              <option value="heatmap">ヒートマップ</option>
              <option value="3d-extrusion">3D立体表示</option>
              <option value="choropleth">段階区分図</option>
              <option value="point-cluster">ポイント集積</option>
            </select>
            <button @click="toggleDataPanel" class="text-sm bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded">
              データパネル {{ showDataPanel ? '非表示' : '表示' }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- データコントロールパネル -->
    <div v-if="showDataPanel" class="data-panel bg-white shadow-lg z-40 absolute top-16 left-0 w-80 h-full overflow-y-auto">
      <div class="p-4">
        <h3 class="text-lg font-bold text-gray-800 mb-4">📊 データ設定</h3>
        
        <!-- データ種別設定 -->
        <div class="mb-6">
          <h4 class="font-semibold text-gray-700 mb-2">表示データ</h4>
          <div class="space-y-2">
            <div v-for="dataOption in dataOptions" :key="dataOption.value" 
                 class="flex items-center">
              <input type="radio" :value="dataOption.value" v-model="selectedDataType" 
                     @change="updateMapData" class="mr-2">
              <label class="text-sm text-gray-700">{{ dataOption.label }}</label>
            </div>
          </div>
        </div>

        <!-- 可視化設定 -->
        <div class="mb-6">
          <h4 class="font-semibold text-gray-700 mb-2">可視化方法</h4>
          <div class="space-y-2">
            <div v-for="vizOption in visualizationOptions" :key="vizOption.value" 
                 class="flex items-center">
              <input type="radio" :value="vizOption.value" v-model="selectedVisualization" 
                     @change="updateVisualization" class="mr-2">
              <label class="text-sm text-gray-700">{{ vizOption.label }}</label>
            </div>
          </div>
        </div>

        <!-- スタイル設定 -->
        <div class="mb-6">
          <h4 class="font-semibold text-gray-700 mb-2">色彩・スタイル</h4>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-gray-600 mb-1">カラーパレット</label>
              <select v-model="selectedColorScheme" @change="updateColors" class="w-full text-sm border rounded px-2 py-1">
                <option value="viridis">Viridis（青→緑→黄）</option>
                <option value="plasma">Plasma（紫→ピンク→黄）</option>
                <option value="cool">Cool（青→水色）</option>
                <option value="warm">Warm（赤→オレンジ）</option>
                <option value="red-blue">Red-Blue（赤→青）</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">透明度: {{ opacity }}%</label>
              <input type="range" v-model="opacity" @input="updateOpacity" min="0" max="100" class="w-full">
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">高さ倍率: {{ heightMultiplier }}x</label>
              <input type="range" v-model="heightMultiplier" @input="updateHeightMultiplier" min="0.1" max="5" step="0.1" class="w-full">
            </div>
          </div>
        </div>

        <!-- 現在のデータ情報 -->
        <div class="bg-gray-50 rounded-lg p-3">
          <h5 class="font-semibold text-gray-800 mb-2">{{ getCurrentDataInfo().title }}</h5>
          <p class="text-xs text-gray-600 mb-2">{{ getCurrentDataInfo().description }}</p>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div>
              <p class="text-gray-500">最大値</p>
              <p class="font-semibold">{{ getCurrentDataInfo().max }}</p>
            </div>
            <div>
              <p class="text-gray-500">最小値</p>
              <p class="font-semibold">{{ getCurrentDataInfo().min }}</p>
            </div>
            <div>
              <p class="text-gray-500">平均値</p>
              <p class="font-semibold">{{ getCurrentDataInfo().avg }}</p>
            </div>
            <div>
              <p class="text-gray-500">データ更新</p>
              <p class="font-semibold">{{ getCurrentDataInfo().updated }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 地図本体 -->
    <div class="map-wrapper" :class="{ 'with-panel': showDataPanel }">
      <div id="map" class="w-full h-full"></div>
      
      <!-- 地図上のコントロール -->
      <div class="map-controls absolute top-4 right-4 space-y-2">
        <button @click="resetView" class="bg-white hover:bg-gray-50 shadow-md rounded-md p-2 text-sm">
          🎯 初期位置
        </button>
        <button @click="toggle3D" class="bg-white hover:bg-gray-50 shadow-md rounded-md p-2 text-sm">
          {{ is3D ? '2D表示' : '3D表示' }}
        </button>
        <button @click="toggleSatellite" class="bg-white hover:bg-gray-50 shadow-md rounded-md p-2 text-sm">
          {{ isSatellite ? '地図' : '衛星' }}
        </button>
      </div>

      <!-- 凡例 -->
      <div class="legend absolute bottom-4 left-4 bg-white bg-opacity-90 rounded-lg p-3 shadow-lg">
        <h6 class="font-semibold text-gray-800 mb-2 text-sm">{{ getCurrentDataInfo().title }}</h6>
        <div class="legend-gradient h-4 w-32 rounded mb-2" :style="getLegendGradient()"></div>
        <div class="flex justify-between text-xs text-gray-600">
          <span>{{ getCurrentDataInfo().min }}</span>
          <span>{{ getCurrentDataInfo().max }}</span>
        </div>
        <p class="text-xs text-gray-500 mt-1">{{ getCurrentDataInfo().unit }}</p>
      </div>

      <!-- ツールチップ -->
      <div v-if="tooltip.visible" class="tooltip absolute bg-black bg-opacity-80 text-white text-sm p-2 rounded pointer-events-none z-50"
           :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
        <div class="font-semibold">{{ tooltip.area }}</div>
        <div>{{ tooltip.dataLabel }}: {{ tooltip.value }}</div>
      </div>
    </div>

    <!-- データローディング表示 -->
    <div v-if="isLoading" class="loading-overlay absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
      <div class="bg-white rounded-lg p-6 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-700">データを読み込み中...</p>
      </div>
    </div>
  </div>
</template>

<script>
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

export default {
  name: 'Map',
  data() {
    return {
      map: null,
      isLoading: false,
      showDataPanel: true,
      is3D: true,
      isSatellite: false,
      selectedDataType: 'population',
      selectedVisualization: '3d-extrusion',
      selectedColorScheme: 'viridis',
      opacity: 80,
      heightMultiplier: 2.0,
      
      tooltip: {
        visible: false,
        x: 0,
        y: 0,
        area: '',
        dataLabel: '',
        value: ''
      },

      dataOptions: [
        { value: 'population', label: '人口密度（人/km²）' },
        { value: 'age', label: '高齢化率（%）' },
        { value: 'income', label: '平均所得（万円）' },
        { value: 'employment', label: '就業率（%）' },
        { value: 'healthcare', label: '医療施設密度（施設/km²）' },
        { value: 'education', label: '教育施設密度（施設/km²）' }
      ],

      visualizationOptions: [
        { value: 'heatmap', label: 'ヒートマップ' },
        { value: '3d-extrusion', label: '3D立体表示' },
        { value: 'choropleth', label: '段階区分図' },
        { value: 'point-cluster', label: 'ポイント集積' }
      ],

      // サンプル統計データ
      statisticalData: {
        population: {
          title: '人口密度',
          description: '1km²あたりの人口数。市街地や住宅地の集中度を表す',
          unit: '人/km²',
          max: 1250,
          min: 15,
          avg: 165,
          updated: '2024年',
          data: {} // 実際のGeoJSONデータがここに入る
        },
        age: {
          title: '高齢化率',
          description: '65歳以上人口の割合。地域の高齢化進行度を示す',
          unit: '%',
          max: 45.2,
          min: 18.5,
          avg: 32.1,
          updated: '2024年',
          data: {}
        },
        income: {
          title: '平均所得',
          description: '世帯あたりの年間所得額。地域の経済力を表す',
          unit: '万円',
          max: 450,
          min: 180,
          avg: 285,
          updated: '2023年',
          data: {}
        }
      }
    }
  },
  mounted() {
    this.initMap()
  },
  beforeUnmount() {
    if (this.map) {
      this.map.remove()
    }
  },
  methods: {
    initMap() {
      mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja2V5MzU1NSIsImEiOiJjbWYyanB3dHIwYXd5MmpzYmV5bnNkOWpzIn0.25cSxUdKCVRz9nJXmvtDdA'

      this.map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v10',
        center: [134.2378, 35.5017], // 鳥取県の中心座標
        zoom: 8.5,
        pitch: 45,
        bearing: 0,
        antialias: true
      })

      this.map.on('load', () => {
        this.setupMapData()
        this.setupMapEvents()
      })
    },

    setupMapData() {
      this.isLoading = true

      // 鳥取県の市町村境界データを追加（サンプル）
      const tottoriMunicipalitiesData = {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            properties: {
              name: '鳥取市',
              population_density: 320,
              aging_rate: 28.5,
              average_income: 315,
              employment_rate: 78.2,
              healthcare_density: 2.1,
              education_density: 1.8
            },
            geometry: {
              type: 'Polygon',
              coordinates: [[
                [134.15, 35.45],
                [134.35, 35.45],
                [134.35, 35.65],
                [134.15, 35.65],
                [134.15, 35.45]
              ]]
            }
          },
          {
            type: 'Feature',
            properties: {
              name: '米子市',
              population_density: 1250,
              aging_rate: 25.1,
              average_income: 295,
              employment_rate: 82.1,
              healthcare_density: 3.2,
              education_density: 2.4
            },
            geometry: {
              type: 'Polygon',
              coordinates: [[
                [133.25, 35.35],
                [133.45, 35.35],
                [133.45, 35.55],
                [133.25, 35.55],
                [133.25, 35.35]
              ]]
            }
          },
          {
            type: 'Feature',
            properties: {
              name: '倉吉市',
              population_density: 180,
              aging_rate: 32.8,
              average_income: 275,
              employment_rate: 75.5,
              healthcare_density: 1.9,
              education_density: 1.5
            },
            geometry: {
              type: 'Polygon',
              coordinates: [[
                [133.75, 35.40],
                [133.95, 35.40],
                [133.95, 35.60],
                [133.75, 35.60],
                [133.75, 35.40]
              ]]
            }
          },
          {
            type: 'Feature',
            properties: {
              name: '境港市',
              population_density: 890,
              aging_rate: 30.2,
              average_income: 285,
              employment_rate: 79.8,
              healthcare_density: 2.5,
              education_density: 1.7
            },
            geometry: {
              type: 'Polygon',
              coordinates: [[
                [133.20, 35.25],
                [133.30, 35.25],
                [133.30, 35.35],
                [133.20, 35.35],
                [133.20, 35.25]
              ]]
            }
          }
        ]
      }

      // データソースを追加
      this.map.addSource('municipalities', {
        type: 'geojson',
        data: tottoriMunicipalitiesData
      })

      // 初期レイヤーを追加
      this.addVisualizationLayer()
      
      this.isLoading = false
    },

    addVisualizationLayer() {
      // 既存のレイヤーを削除
      if (this.map.getLayer('municipalities-layer')) {
        this.map.removeLayer('municipalities-layer')
      }

      const propertyName = this.getPropertyName()
      
      if (this.selectedVisualization === '3d-extrusion') {
        this.map.addLayer({
          id: 'municipalities-layer',
          type: 'fill-extrusion',
          source: 'municipalities',
          paint: {
            'fill-extrusion-color': [
              'interpolate',
              ['linear'],
              ['get', propertyName],
              0, this.getColorForValue(0),
              500, this.getColorForValue(0.5),
              1000, this.getColorForValue(1)
            ],
            'fill-extrusion-height': [
              '*',
              ['get', propertyName],
              this.heightMultiplier * 10
            ],
            'fill-extrusion-base': 0,
            'fill-extrusion-opacity': this.opacity / 100
          }
        })
      } else if (this.selectedVisualization === 'choropleth') {
        this.map.addLayer({
          id: 'municipalities-layer',
          type: 'fill',
          source: 'municipalities',
          paint: {
            'fill-color': [
              'interpolate',
              ['linear'],
              ['get', propertyName],
              0, this.getColorForValue(0),
              500, this.getColorForValue(0.5),
              1000, this.getColorForValue(1)
            ],
            'fill-opacity': this.opacity / 100
          }
        })
      } else if (this.selectedVisualization === 'heatmap') {
        // ヒートマップの場合はポイントデータが必要
        this.addHeatmapLayer()
      }
    },

    addHeatmapLayer() {
      // 市町村の中心点データを生成
      const pointData = {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            properties: { value: 320 },
            geometry: { type: 'Point', coordinates: [134.25, 35.55] }
          },
          {
            type: 'Feature',
            properties: { value: 1250 },
            geometry: { type: 'Point', coordinates: [133.35, 35.45] }
          },
          {
            type: 'Feature',
            properties: { value: 180 },
            geometry: { type: 'Point', coordinates: [133.85, 35.50] }
          },
          {
            type: 'Feature',
            properties: { value: 890 },
            geometry: { type: 'Point', coordinates: [133.25, 35.30] }
          }
        ]
      }

      if (!this.map.getSource('heatmap-data')) {
        this.map.addSource('heatmap-data', {
          type: 'geojson',
          data: pointData
        })
      }

      this.map.addLayer({
        id: 'municipalities-layer',
        type: 'heatmap',
        source: 'heatmap-data',
        paint: {
          'heatmap-weight': ['get', 'value'],
          'heatmap-intensity': 1,
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(0, 0, 255, 0)',
            0.2, 'rgb(0, 255, 255)',
            0.4, 'rgb(0, 255, 0)',
            0.6, 'rgb(255, 255, 0)',
            0.8, 'rgb(255, 165, 0)',
            1, 'rgb(255, 0, 0)'
          ],
          'heatmap-radius': 50,
          'heatmap-opacity': this.opacity / 100
        }
      })
    },

    setupMapEvents() {
      // ツールチップの表示
      this.map.on('mousemove', 'municipalities-layer', (e) => {
        if (e.features.length > 0) {
          const feature = e.features[0]
          const propertyName = this.getPropertyName()
          
          this.tooltip = {
            visible: true,
            x: e.point.x + 10,
            y: e.point.y - 10,
            area: feature.properties.name,
            dataLabel: this.getCurrentDataInfo().title,
            value: feature.properties[propertyName] + this.getCurrentDataInfo().unit
          }
        }
      })

      this.map.on('mouseleave', 'municipalities-layer', () => {
        this.tooltip.visible = false
      })

      // カーソルスタイルの変更
      this.map.on('mouseenter', 'municipalities-layer', () => {
        this.map.getCanvas().style.cursor = 'pointer'
      })

      this.map.on('mouseleave', 'municipalities-layer', () => {
        this.map.getCanvas().style.cursor = ''
      })
    },

    updateMapData() {
      this.isLoading = true
      setTimeout(() => {
        this.addVisualizationLayer()
        this.isLoading = false
      }, 500)
    },

    updateVisualization() {
      this.addVisualizationLayer()
    },

    updateColors() {
      this.addVisualizationLayer()
    },

    updateOpacity() {
      const layerId = 'municipalities-layer'
      if (this.map.getLayer(layerId)) {
        if (this.selectedVisualization === '3d-extrusion') {
          this.map.setPaintProperty(layerId, 'fill-extrusion-opacity', this.opacity / 100)
        } else if (this.selectedVisualization === 'choropleth') {
          this.map.setPaintProperty(layerId, 'fill-opacity', this.opacity / 100)
        } else if (this.selectedVisualization === 'heatmap') {
          this.map.setPaintProperty(layerId, 'heatmap-opacity', this.opacity / 100)
        }
      }
    },

    updateHeightMultiplier() {
      const layerId = 'municipalities-layer'
      if (this.map.getLayer(layerId) && this.selectedVisualization === '3d-extrusion') {
        const propertyName = this.getPropertyName()
        this.map.setPaintProperty(layerId, 'fill-extrusion-height', [
          '*',
          ['get', propertyName],
          this.heightMultiplier * 10
        ])
      }
    },

    getPropertyName() {
      const propertyMap = {
        population: 'population_density',
        age: 'aging_rate',
        income: 'average_income',
        employment: 'employment_rate',
        healthcare: 'healthcare_density',
        education: 'education_density'
      }
      return propertyMap[this.selectedDataType]
    },

    getCurrentDataInfo() {
      return this.statisticalData[this.selectedDataType] || this.statisticalData.population
    },

    getColorForValue(normalizedValue) {
      const schemes = {
        viridis: normalizedValue < 0.33 ? '#440154' : normalizedValue < 0.67 ? '#21908c' : '#fde725',
        plasma: normalizedValue < 0.33 ? '#0d0887' : normalizedValue < 0.67 ? '#cc4778' : '#f0f921',
        cool: normalizedValue < 0.33 ? '#0000ff' : normalizedValue < 0.67 ? '#0080ff' : '#00ffff',
        warm: normalizedValue < 0.33 ? '#ff0000' : normalizedValue < 0.67 ? '#ff8000' : '#ffff00',
        'red-blue': normalizedValue < 0.33 ? '#ff0000' : normalizedValue < 0.67 ? '#ffffff' : '#0000ff'
      }
      return schemes[this.selectedColorScheme] || schemes.viridis
    },

    getLegendGradient() {
      const gradients = {
        viridis: 'linear-gradient(to right, #440154, #21908c, #fde725)',
        plasma: 'linear-gradient(to right, #0d0887, #cc4778, #f0f921)',
        cool: 'linear-gradient(to right, #0000ff, #0080ff, #00ffff)',
        warm: 'linear-gradient(to right, #ff0000, #ff8000, #ffff00)',
        'red-blue': 'linear-gradient(to right, #ff0000, #ffffff, #0000ff)'
      }
      return `background: ${gradients[this.selectedColorScheme] || gradients.viridis}`
    },

    toggleDataPanel() {
      this.showDataPanel = !this.showDataPanel
    },

    resetView() {
      this.map.flyTo({
        center: [134.2378, 35.5017],
        zoom: 8.5,
        pitch: 45,
        bearing: 0
      })
    },

    toggle3D() {
      this.is3D = !this.is3D
      this.map.flyTo({
        pitch: this.is3D ? 45 : 0
      })
    },

    toggleSatellite() {
      this.isSatellite = !this.isSatellite
      this.map.setStyle(this.isSatellite ? 
        'mapbox://styles/mapbox/satellite-v9' : 
        'mapbox://styles/mapbox/light-v10'
      )
      
      // スタイル変更後にデータを再追加
      this.map.once('styledata', () => {
        this.setupMapData()
      })
    }
  }
}
</script>

<style scoped>
.map-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.map-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
}

.data-panel {
  position: fixed;
  top: 64px;
  left: 0;
  width: 320px;
  height: calc(100vh - 64px);
  z-index: 40;
  overflow-y: auto;
}

.map-wrapper {
  position: absolute;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  transition: left 0.3s ease;
}

.map-wrapper.with-panel {
  left: 320px;
}

#map {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 30;
}

.legend {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  z-index: 30;
}

.tooltip {
  z-index: 60;
}

.loading-overlay {
  z-index: 70;
}

/* スクロールバーのスタイル */
.data-panel::-webkit-scrollbar {
  width: 6px;
}

.data-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.data-panel::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.data-panel::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>