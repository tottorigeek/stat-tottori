<template>
  <div class="hello">
    <h2>{{ message }}</h2>
    <p>
      鳥取県の地域統計データを体系的に分析し、地域の現状とトレンドを可視化するプロジェクトです。
    </p>
    <div class="features">
      <h3>主な機能</h3>
      <ul>
        <li>人口動態分析</li>
        <li>経済指標可視化</li>
        <li>社会福祉データ分析</li>
        <li>教育・文化統計</li>
        <li>環境・インフラデータ</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  data() {
    return {
      message: 'Hello World - 鳥取県統計プロジェクト'
    }
  }
}
</script>

<style scoped>
.hello {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #e74c3c;
  margin-bottom: 20px;
}

p {
  font-size: 18px;
  line-height: 1.6;
  color: #34495e;
  margin-bottom: 30px;
}

.features {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 30px;
}

.features h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.features ul {
  list-style-type: none;
  padding: 0;
}

.features li {
  background-color: #ffffff;
  margin: 10px 0;
  padding: 10px 15px;
  border-left: 4px solid #42b883;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: left;
}
</style>