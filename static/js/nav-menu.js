// Navigation Menu Vue Component
const NavMenuComponent = {
  template: `
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
  `,
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
};

// Initialize Vue app with navigation
function initNavMenu(elementId = '#nav-menu-app') {
  const { createApp } = Vue;
  
  const app = createApp({
    components: {
      'nav-menu': NavMenuComponent
    },
    data() {
      return {
        currentPath: window.location.pathname
      }
    },
    methods: {
      onMenuChanged(path) {
        this.currentPath = path;
      }
    }
  });
  
  app.mount(elementId);
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  const navContainer = document.getElementById('nav-menu-app');
  if (navContainer) {
    initNavMenu();
  }
});
