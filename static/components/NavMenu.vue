<template>
  <nav class="nav-menu">
    <ul>
      <li v-for="item in menuItems" :key="item.path">
        <a 
          :href="item.path" 
          :class="{ active: isActive(item.path) }"
          @click="setActive(item.path)"
        >
          {{ item.icon }} {{ item.name }}
        </a>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: 'NavMenu',
  props: {
    currentPath: {
      type: String,
      default: '/'
    }
  },
  data() {
    return {
      activePath: this.currentPath,
      menuItems: [
        { path: '/', name: 'Home', icon: '🏠' },
        { path: '/connect-plus', name: 'Connect++', icon: '🔗' },
        { path: '/connect-manager', name: 'Connect Manager', icon: '⚙️' },
        { path: '/connect-display', name: 'Connect Display', icon: '📺' },
        { path: '/fleet-data-manager', name: 'Fleet Data Manager', icon: '📊' },
        { path: '/fleet-config-manager', name: 'Fleet Config Manager', icon: '🔧' },
        { path: '/fleet-software-manager', name: 'Fleet Software Manager', icon: '💿' },
        { path: '/fleet-workshop-manager', name: 'Fleet Workshop Manager', icon: '🔧' },
        { path: '/docs', name: 'API Docs', icon: '📚' }
      ]
    }
  },
  mounted() {
    // Auto-detect current path from URL
    this.activePath = window.location.pathname;
  },
  methods: {
    isActive(path) {
      return this.activePath === path;
    },
    setActive(path) {
      this.activePath = path;
      this.$emit('menu-changed', path);
    }
  }
}
</script>

<style scoped>
.nav-menu {
  background: #2c3e50;
  padding: 0;
  margin: 0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.nav-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
}

.nav-menu li {
  margin: 0;
}

.nav-menu a {
  display: block;
  padding: 15px 20px;
  color: white;
  text-decoration: none;
  transition: background 0.3s;
}

.nav-menu a:hover {
  background: #34495e;
}

.nav-menu a.active {
  background: #34495e;
  font-weight: bold;
}

/* Module-specific active colors */
.nav-menu a[href="/connect-plus"].active {
  background: #3498db;
}

.nav-menu a[href="/connect-manager"].active {
  background: #e74c3c;
}

.nav-menu a[href="/connect-display"].active {
  background: #9b59b6;
}

.nav-menu a[href="/fleet-data-manager"].active {
  background: #27ae60;
}

.nav-menu a[href="/fleet-config-manager"].active {
  background: #4caf50;
}

.nav-menu a[href="/fleet-software-manager"].active {
  background: #34495e;
}

.nav-menu a[href="/fleet-workshop-manager"].active {
  background: #d35400;
}

/* Responsive design */
@media (max-width: 768px) {
  .nav-menu ul {
    flex-direction: column;
  }
  
  .nav-menu a {
    padding: 12px 15px;
    font-size: 14px;
  }
}
</style>
