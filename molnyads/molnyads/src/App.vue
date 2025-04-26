<template>
  <div id="app">
    <nav>
      <router-link to="/" exact-active-class="active">Главная</router-link> |
      <router-link to="/balance" exact-active-class="active">Баланс</router-link> |
      <router-link to="/mychannels" exact-active-class="active">Мои каналы</router-link> |
      <router-link to="/adcatalog" exact-active-class="active">Каталог реклам</router-link> |
      <router-link to="/catalog" exact-active-class="active">Каталог</router-link> |
      <router-link to="/myad" exact-active-class="active">Детали покупки</router-link> |
      <router-link to="/profile" exact-active-class="active">Профиль</router-link> |
      <router-link to="/channel" exact-active-class="active">Страница канала</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

nav a.active {
  color: #42b983;
}
</style>
