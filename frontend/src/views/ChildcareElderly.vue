<template>
  <div class="container mx-auto px-4 py-8">
    <!-- ページヘッダー -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">👨‍👩‍👧‍👦 子育て・高齢者支援</h1>
      <p class="text-gray-600">子育て世帯と高齢者の皆さまをサポートする情報をお届けします</p>
    </div>

    <!-- タブナビゲーション -->
    <div class="mb-8">
      <nav class="flex space-x-8 border-b border-gray-200">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          <span>{{ tab.icon }}</span>
          <span>{{ tab.name }}</span>
        </button>
      </nav>
    </div>

    <!-- 子育て支援タブ -->
    <div v-if="activeTab === 'childcare'" class="space-y-8">
      <!-- 保育施設情報 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">保育施設空き状況</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="facility in childcareFacilities" :key="facility.name" class="p-4 border rounded-lg" :class="getFacilityClass(facility.availability)">
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-semibold text-gray-800">{{ facility.name }}</h4>
              <span :class="getAvailabilityColor(facility.availability)" class="px-2 py-1 text-xs rounded">
                {{ facility.availability }}
              </span>
            </div>
            <p class="text-sm text-gray-600 mb-2">{{ facility.type }} | {{ facility.age }}</p>
            <p class="text-sm text-gray-600 mb-2">定員: {{ facility.capacity }}名</p>
            <p class="text-sm font-medium text-blue-600">月額: {{ facility.fee }}円〜</p>
          </div>
        </div>
      </div>

      <!-- 子育て支援制度 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">子育て支援制度</h3>
        <div class="space-y-4">
          <div v-for="support in childrearSupport" :key="support.name" class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex justify-between items-start">
              <div>
                <h4 class="font-semibold text-gray-800">{{ support.name }}</h4>
                <p class="text-sm text-gray-600 mt-1">{{ support.description }}</p>
              </div>
              <span class="text-lg font-bold text-blue-600">{{ support.amount }}</span>
            </div>
            <div class="mt-2 text-xs text-gray-500">
              対象: {{ support.target }} | 申請: {{ support.application }}
            </div>
          </div>
        </div>
      </div>

      <!-- 子育てイベント・サークル -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">子育てイベント・サークル</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="event in childcareEvents" :key="event.name" class="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div class="flex items-start justify-between">
              <div>
                <h4 class="font-semibold text-gray-800">{{ event.name }}</h4>
                <p class="text-sm text-gray-600 mt-1">{{ event.description }}</p>
                <div class="mt-2 text-sm">
                  <p class="text-gray-600">📅 {{ event.schedule }}</p>
                  <p class="text-gray-600">📍 {{ event.location }}</p>
                </div>
              </div>
              <span class="text-green-600 font-medium text-sm">{{ event.fee }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 高齢者支援タブ -->
    <div v-if="activeTab === 'elderly'" class="space-y-8">
      <!-- 介護施設情報 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">介護施設空き状況</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="facility in elderlyFacilities" :key="facility.name" class="p-4 border rounded-lg" :class="getFacilityClass(facility.availability)">
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-semibold text-gray-800">{{ facility.name }}</h4>
              <span :class="getAvailabilityColor(facility.availability)" class="px-2 py-1 text-xs rounded">
                {{ facility.availability }}
              </span>
            </div>
            <p class="text-sm text-gray-600 mb-2">{{ facility.type }}</p>
            <p class="text-sm text-gray-600 mb-2">定員: {{ facility.capacity }}名</p>
            <p class="text-sm font-medium text-blue-600">月額: {{ facility.fee }}円〜</p>
          </div>
        </div>
      </div>

      <!-- 高齢者支援サービス -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">高齢者支援サービス</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="service in elderlyServices" :key="service.name" class="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h4 class="font-semibold text-gray-800">{{ service.name }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ service.description }}</p>
            <div class="mt-3">
              <p class="text-sm text-gray-600">💰 料金: {{ service.fee }}</p>
              <p class="text-sm text-gray-600">📞 連絡先: {{ service.contact }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 健康・生きがい活動 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">健康・生きがい活動</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="activity in healthActivities" :key="activity.name" class="p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <h4 class="font-semibold text-gray-800">{{ activity.name }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ activity.description }}</p>
            <div class="mt-3">
              <p class="text-sm text-gray-600">📅 {{ activity.schedule }}</p>
              <p class="text-sm text-gray-600">📍 {{ activity.location }}</p>
              <p class="text-sm text-green-600 font-medium">{{ activity.fee }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 相談・お問い合わせ -->
    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-8">
      <h3 class="text-xl font-bold text-yellow-800 mb-4">📞 相談・お問い合わせ</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-semibold text-yellow-800 mb-2">子育て相談</h4>
          <div class="space-y-1 text-sm text-yellow-700">
            <p>鳥取市子育て支援センター: 0857-20-3145</p>
            <p>子育て何でも相談: 0857-20-0122</p>
            <p>受付時間: 平日 9:00-17:00</p>
          </div>
        </div>
        <div>
          <h4 class="font-semibold text-yellow-800 mb-2">高齢者相談</h4>
          <div class="space-y-1 text-sm text-yellow-700">
            <p>地域包括支援センター: 0857-20-3456</p>
            <p>介護保険相談: 0857-20-3789</p>
            <p>受付時間: 平日 8:30-17:15</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChildcareElderly',
  data() {
    return {
      activeTab: 'childcare',
      tabs: [
        { id: 'childcare', name: '子育て支援', icon: '👶' },
        { id: 'elderly', name: '高齢者支援', icon: '👴' }
      ],
      childcareFacilities: [
        { name: '鳥取保育園', type: '認可保育園', age: '0-5歳', capacity: 120, fee: '20000', availability: '空きあり' },
        { name: 'さくら幼稚園', type: '認定こども園', age: '3-5歳', capacity: 90, fee: '25000', availability: '満員' },
        { name: 'つばき保育所', type: '小規模保育', age: '0-2歳', capacity: 19, fee: '18000', availability: '空きあり' },
        { name: 'みどり幼稚園', type: '幼稚園', age: '3-5歳', capacity: 80, fee: '22000', availability: '若干名' },
        { name: 'すみれ保育園', type: '認可保育園', age: '0-5歳', capacity: 100, fee: '19000', availability: '空きあり' },
        { name: 'たんぽぽ園', type: '企業主導型', age: '0-3歳', capacity: 40, fee: '30000', availability: '満員' }
      ],
      childrearSupport: [
        {
          name: '児童手当',
          description: '中学校修了まで支給される手当',
          amount: '月額1.5万円',
          target: '中学生まで',
          application: '市町村窓口'
        },
        {
          name: '子ども医療費助成',
          description: '18歳まで医療費を助成',
          amount: '自己負担なし',
          target: '18歳まで',
          application: '自動適用'
        },
        {
          name: '保育料軽減制度',
          description: '第2子以降の保育料を軽減',
          amount: '最大50%減免',
          target: '多子世帯',
          application: '保育施設申込時'
        },
        {
          name: '出産・子育て応援交付金',
          description: '出産・育児の経済的支援',
          amount: '計10万円',
          target: '妊婦・新生児',
          application: '市町村窓口'
        }
      ],
      childcareEvents: [
        {
          name: 'ママサークル「ひまわり」',
          description: '0-3歳の子どもとお母さんの交流会',
          schedule: '毎週火曜日 10:00-12:00',
          location: '中央公民館',
          fee: '無料'
        },
        {
          name: '親子リトミック教室',
          description: '音楽を通じた親子の触れ合い',
          schedule: '第2・4土曜日 10:30-11:30',
          location: '文化センター',
          fee: '500円'
        },
        {
          name: '子育て相談会',
          description: '保健師による育児相談',
          schedule: '第1金曜日 13:30-15:30',
          location: '保健所',
          fee: '無料'
        },
        {
          name: '絵本読み聞かせ会',
          description: '図書館スタッフによる読み聞かせ',
          schedule: '毎週土曜日 14:00-14:30',
          location: '中央図書館',
          fee: '無料'
        }
      ],
      elderlyFacilities: [
        { name: 'ケアハウス鳥取', type: '軽費老人ホーム', capacity: 50, fee: '80000', availability: '空きあり' },
        { name: '特養やまもと', type: '特別養護老人ホーム', capacity: 80, fee: '120000', availability: '待機中' },
        { name: 'グループホームさくら', type: 'グループホーム', capacity: 18, fee: '150000', availability: '空きあり' },
        { name: 'デイサービス太陽', type: 'デイサービス', capacity: 30, fee: '8000', availability: '空きあり' },
        { name: '有料老人ホーム緑風', type: '住宅型有料老人ホーム', capacity: 40, fee: '180000', availability: '若干名' },
        { name: 'ショートステイ花', type: 'ショートステイ', capacity: 20, fee: '12000', availability: '空きあり' }
      ],
      elderlyServices: [
        {
          name: '配食サービス',
          description: '栄養バランスの取れた食事を自宅まで配達',
          fee: '1食500円〜',
          contact: '0857-20-3456'
        },
        {
          name: '買い物代行サービス',
          description: '日用品・食料品の買い物を代行',
          fee: '1回1000円〜',
          contact: '0857-20-4567'
        },
        {
          name: '見守りサービス',
          description: '定期的な安否確認と緊急時対応',
          fee: '月額3000円〜',
          contact: '0857-20-5678'
        },
        {
          name: '訪問入浴サービス',
          description: '自宅での入浴介助サービス',
          fee: '1回12000円〜',
          contact: '0857-20-6789'
        }
      ],
      healthActivities: [
        {
          name: 'シルバー体操教室',
          description: '高齢者向けの軽体操',
          schedule: '毎週月・木曜日 10:00-11:00',
          location: '総合体育館',
          fee: '月額2000円'
        },
        {
          name: '健康麻雀サロン',
          description: '認知症予防に効果的な健康麻雀',
          schedule: '毎週水・金曜日 13:00-16:00',
          location: '老人福祉センター',
          fee: '1回500円'
        },
        {
          name: '園芸療法教室',
          description: '植物を育てる喜びを通じた健康づくり',
          schedule: '第2・4土曜日 9:00-11:00',
          location: '農業体験施設',
          fee: '月額3000円'
        },
        {
          name: 'カラオケサークル',
          description: '歌を通じた仲間づくり',
          schedule: '毎週火曜日 14:00-16:00',
          location: '公民館',
          fee: '月額1500円'
        }
      ]
    }
  },
  methods: {
    getFacilityClass(availability) {
      switch(availability) {
        case '空きあり': return 'bg-green-50 border-green-200'
        case '若干名': return 'bg-yellow-50 border-yellow-200'
        case '満員': case '待機中': return 'bg-red-50 border-red-200'
        default: return 'bg-gray-50 border-gray-200'
      }
    },
    getAvailabilityColor(availability) {
      switch(availability) {
        case '空きあり': return 'bg-green-500 text-white'
        case '若干名': return 'bg-yellow-500 text-white'
        case '満員': case '待機中': return 'bg-red-500 text-white'
        default: return 'bg-gray-500 text-white'
      }
    }
  }
}
</script>