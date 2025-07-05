/**
 * Technology Stack Integration Layer
 * 
 * Provides unified access to multiple frontend and backend technologies:
 * - React/jQuery/JS frameworks integration
 * - Database connectors (SQL, NoSQL, MySQL)
 * - Backend services (Django, Ruby on Rails, Spring)
 * - Responsive design utilities
 * - HTTPS/Security helpers
 */

import axios from 'axios';
import { getBaseUrl } from '../utils/config';

// Base configuration
const baseUrl = getBaseUrl();
const apiPath = '/api';

// Common headers with security defaults
const secureHeaders = {
  'Content-Type': 'application/json',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
};

/**
 * HTTP/HTTPS Service for secure communication
 */
const httpService = {
  /**
   * Create secure axios instance with proper configuration
   * @param {Object} options - Configuration options
   * @returns {Object} - Configured axios instance
   */
  createSecureClient(options = {}) {
    return axios.create({
      baseURL: options.baseURL || `${baseUrl}${apiPath}`,
      timeout: options.timeout || 30000,
      headers: {
        ...secureHeaders,
        ...(options.headers || {})
      },
      withCredentials: true,
    });
  },

  /**
   * Make a secure GET request
   * @param {string} url - Endpoint URL
   * @param {Object} params - Query parameters
   * @param {Object} options - Request options
   * @returns {Promise} - Request promise
   */
  async get(url, params = {}, options = {}) {
    const client = this.createSecureClient(options);
    try {
      const response = await client.get(url, { params });
      return response.data;
    } catch (error) {
      console.error('HTTP GET error:', error);
      throw this._formatError(error);
    }
  },

  /**
   * Make a secure POST request
   * @param {string} url - Endpoint URL
   * @param {Object} data - Request payload
   * @param {Object} options - Request options
   * @returns {Promise} - Request promise
   */
  async post(url, data = {}, options = {}) {
    const client = this.createSecureClient(options);
    try {
      const response = await client.post(url, data);
      return response.data;
    } catch (error) {
      console.error('HTTP POST error:', error);
      throw this._formatError(error);
    }
  },

  /**
   * Make a secure PUT request
   * @param {string} url - Endpoint URL
   * @param {Object} data - Request payload
   * @param {Object} options - Request options
   * @returns {Promise} - Request promise
   */
  async put(url, data = {}, options = {}) {
    const client = this.createSecureClient(options);
    try {
      const response = await client.put(url, data);
      return response.data;
    } catch (error) {
      console.error('HTTP PUT error:', error);
      throw this._formatError(error);
    }
  },

  /**
   * Make a secure DELETE request
   * @param {string} url - Endpoint URL
   * @param {Object} options - Request options
   * @returns {Promise} - Request promise
   */
  async delete(url, options = {}) {
    const client = this.createSecureClient(options);
    try {
      const response = await client.delete(url);
      return response.data;
    } catch (error) {
      console.error('HTTP DELETE error:', error);
      throw this._formatError(error);
    }
  },

  /**
   * Format error for consistent handling
   * @private
   * @param {Error} error - Error object
   * @returns {Object} - Formatted error
   */
  _formatError(error) {
    return {
      message: error.response?.data?.detail || error.message || 'Unknown error',
      status: error.response?.status || 500,
      data: error.response?.data,
    };
  }
};

/**
 * SQL Database Integration
 * Supports MySQL, PostgreSQL, SQLite operations
 */
const sqlService = {
  /**
   * Execute a SQL query via API
   * @param {string} query - SQL query string
   * @param {Object} params - Query parameters
   * @param {string} dbType - Database type (mysql, postgres, sqlite)
   * @returns {Promise<Array>} - Query results
   */
  async executeQuery(query, params = {}, dbType = 'mysql') {
    try {
      const response = await httpService.post('/db/sql/execute', {
        query,
        params,
        db_type: dbType
      });
      return response.results;
    } catch (error) {
      console.error('SQL query error:', error);
      throw error;
    }
  },

  /**
   * Get database schema information
   * @param {string} dbType - Database type
   * @returns {Promise<Object>} - Schema information
   */
  async getSchema(dbType = 'mysql') {
    try {
      return await httpService.get('/db/sql/schema', { db_type: dbType });
    } catch (error) {
      console.error('Schema retrieval error:', error);
      throw error;
    }
  },

  /**
   * Test database connection
   * @param {Object} connectionParams - Connection parameters
   * @returns {Promise<Object>} - Connection status
   */
  async testConnection(connectionParams) {
    try {
      return await httpService.post('/db/sql/test-connection', connectionParams);
    } catch (error) {
      console.error('Connection test error:', error);
      throw error;
    }
  }
};

/**
 * NoSQL Database Integration
 * Supports MongoDB, Firebase, Redis operations
 */
const noSqlService = {
  /**
   * Create or update a document
   * @param {string} collection - Collection/table name
   * @param {string} id - Document ID (optional for new documents)
   * @param {Object} data - Document data
   * @param {string} dbType - NoSQL database type
   * @returns {Promise<Object>} - Operation result
   */
  async saveDocument(collection, data, id = null, dbType = 'mongodb') {
    try {
      const endpoint = id ? 
        `/db/nosql/${dbType}/${collection}/${id}` : 
        `/db/nosql/${dbType}/${collection}`;
      
      const method = id ? 'put' : 'post';
      return await httpService[method](endpoint, data);
    } catch (error) {
      console.error('NoSQL save error:', error);
      throw error;
    }
  },

  /**
   * Get a document by ID
   * @param {string} collection - Collection/table name
   * @param {string} id - Document ID
   * @param {string} dbType - NoSQL database type
   * @returns {Promise<Object>} - Document data
   */
  async getDocument(collection, id, dbType = 'mongodb') {
    try {
      return await httpService.get(`/db/nosql/${dbType}/${collection}/${id}`);
    } catch (error) {
      console.error('NoSQL get error:', error);
      throw error;
    }
  },

  /**
   * Query documents with filters
   * @param {string} collection - Collection/table name
   * @param {Object} query - Query filters
   * @param {Object} options - Query options (sort, limit, etc.)
   * @param {string} dbType - NoSQL database type
   * @returns {Promise<Array>} - Matching documents
   */
  async queryDocuments(collection, query = {}, options = {}, dbType = 'mongodb') {
    try {
      return await httpService.post(`/db/nosql/${dbType}/${collection}/query`, {
        query,
        options
      });
    } catch (error) {
      console.error('NoSQL query error:', error);
      throw error;
    }
  },

  /**
   * Delete a document
   * @param {string} collection - Collection/table name
   * @param {string} id - Document ID
   * @param {string} dbType - NoSQL database type
   * @returns {Promise<Object>} - Operation result
   */
  async deleteDocument(collection, id, dbType = 'mongodb') {
    try {
      return await httpService.delete(`/db/nosql/${dbType}/${collection}/${id}`);
    } catch (error) {
      console.error('NoSQL delete error:', error);
      throw error;
    }
  }
};

/**
 * jQuery Integration Layer
 * Provides jQuery-like functionality with modern React integration
 */
const jQueryBridge = {
  /**
   * Select DOM elements (React-friendly)
   * @param {string} selector - CSS selector
   * @param {Element} context - Context element
   * @returns {Object} - jQuery-like object
   */
  $(selector, context = document) {
    const elements = context.querySelectorAll(selector);
    
    // Create jQuery-like object with chainable methods
    const jqObject = {
      elements: Array.from(elements),
      
      // DOM manipulation
      html(content) {
        if (content === undefined) {
          return this.elements[0]?.innerHTML || '';
        }
        this.elements.forEach(el => { el.innerHTML = content; });
        return this;
      },
      
      text(content) {
        if (content === undefined) {
          return this.elements[0]?.textContent || '';
        }
        this.elements.forEach(el => { el.textContent = content; });
        return this;
      },
      
      addClass(className) {
        this.elements.forEach(el => el.classList.add(className));
        return this;
      },
      
      removeClass(className) {
        this.elements.forEach(el => el.classList.remove(className));
        return this;
      },
      
      toggleClass(className) {
        this.elements.forEach(el => el.classList.toggle(className));
        return this;
      },
      
      attr(name, value) {
        if (value === undefined) {
          return this.elements[0]?.getAttribute(name);
        }
        this.elements.forEach(el => { el.setAttribute(name, value); });
        return this;
      },
      
      // Events
      on(eventType, handler) {
        this.elements.forEach(el => {
          el.addEventListener(eventType, handler);
        });
        return this;
      },
      
      off(eventType, handler) {
        this.elements.forEach(el => {
          el.removeEventListener(eventType, handler);
        });
        return this;
      },
      
      // Ajax (using our HTTP service)
      ajax(options) {
        return httpService.post('/proxy/ajax', options);
      }
    };
    
    return jqObject;
  },
  
  /**
   * Check if element is ready
   * @param {Function} callback - Function to run when DOM is ready
   */
  ready(callback) {
    if (document.readyState !== 'loading') {
      callback();
    } else {
      document.addEventListener('DOMContentLoaded', callback);
    }
  },
  
  /**
   * Create a new jQuery-compatible plugin
   * @param {string} name - Plugin name
   * @param {Function} implementation - Plugin implementation
   */
  plugin(name, implementation) {
    this.$[name] = implementation;
  }
};

/**
 * Backend Framework Integration Services
 */
const backendServices = {
  /**
   * Django backend integration
   */
  django: {
    /**
     * Call a Django view
     * @param {string} viewName - Django view name
     * @param {Object} data - Request data
     * @returns {Promise<Object>} - Response data
     */
    callView(viewName, data = {}) {
      return httpService.post(`/django/view/${viewName}`, data);
    },
    
    /**
     * Get Django model data
     * @param {string} modelName - Django model name
     * @param {Object} filters - Query filters
     * @returns {Promise<Array>} - Model instances
     */
    getModelData(modelName, filters = {}) {
      return httpService.get(`/django/model/${modelName}`, filters);
    },
    
    /**
     * Execute Django admin action
     * @param {string} modelName - Django model name
     * @param {string} actionName - Action name
     * @param {Array} ids - Object IDs
     * @returns {Promise<Object>} - Action result
     */
    adminAction(modelName, actionName, ids = []) {
      return httpService.post(`/django/admin/${modelName}/${actionName}`, { ids });
    }
  },
  
  /**
   * Ruby on Rails backend integration
   */
  rails: {
    /**
     * Call a Rails controller action
     * @param {string} controller - Controller name
     * @param {string} action - Action name
     * @param {Object} data - Request data
     * @returns {Promise<Object>} - Response data
     */
    callAction(controller, action, data = {}) {
      return httpService.post(`/rails/${controller}/${action}`, data);
    },
    
    /**
     * Get Rails model data
     * @param {string} model - Model name
     * @param {Object} conditions - Query conditions
     * @returns {Promise<Array>} - Model instances
     */
    getModelData(model, conditions = {}) {
      return httpService.get(`/rails/model/${model}`, conditions);
    },
    
    /**
     * Execute Rails ActiveJob
     * @param {string} jobName - Job name
     * @param {Array} args - Job arguments
     * @returns {Promise<Object>} - Job status
     */
    performJob(jobName, args = []) {
      return httpService.post(`/rails/job/${jobName}`, { args });
    }
  },
  
  /**
   * Spring backend integration
   */
  spring: {
    /**
     * Call a Spring controller endpoint
     * @param {string} path - Controller path
     * @param {Object} data - Request data
     * @param {string} method - HTTP method
     * @returns {Promise<Object>} - Response data
     */
    callController(path, data = {}, method = 'post') {
      return httpService[method.toLowerCase()](`/spring/${path}`, data);
    },
    
    /**
     * Get Spring JPA entity data
     * @param {string} entity - Entity name
     * @param {Object} params - Query parameters
     * @returns {Promise<Array>} - Entity instances
     */
    getEntityData(entity, params = {}) {
      return httpService.get(`/spring/data/${entity}`, params);
    },
    
    /**
     * Execute Spring Batch job
     * @param {string} jobName - Job name
     * @param {Object} params - Job parameters
     * @returns {Promise<Object>} - Job execution status
     */
    executeJob(jobName, params = {}) {
      return httpService.post(`/spring/batch/${jobName}`, params);
    }
  }
};

/**
 * Responsive Web Design utilities
 */
const responsiveUtils = {
  /**
   * Current breakpoint based on screen size
   * @returns {string} - Current breakpoint (xs, sm, md, lg, xl)
   */
  getCurrentBreakpoint() {
    const width = window.innerWidth;
    if (width < 576) return 'xs';
    if (width < 768) return 'sm';
    if (width < 992) return 'md';
    if (width < 1200) return 'lg';
    return 'xl';
  },
  
  /**
   * Check if current screen matches a breakpoint
   * @param {string} breakpoint - Breakpoint to check
   * @returns {boolean} - Whether screen matches the breakpoint
   */
  isBreakpoint(breakpoint) {
    return this.getCurrentBreakpoint() === breakpoint;
  },
  
  /**
   * Check if screen is mobile
   * @returns {boolean} - Whether screen is mobile size
   */
  isMobile() {
    const bp = this.getCurrentBreakpoint();
    return bp === 'xs' || bp === 'sm';
  },
  
  /**
   * Check if element is visible in viewport
   * @param {Element} element - DOM element
   * @returns {boolean} - Whether element is in viewport
   */
  isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    );
  },
  
  /**
   * Register a breakpoint change listener
   * @param {Function} callback - Callback function
   * @returns {Function} - Unregister function
   */
  onBreakpointChange(callback) {
    let currentBreakpoint = this.getCurrentBreakpoint();
    
    const handler = () => {
      const newBreakpoint = this.getCurrentBreakpoint();
      if (newBreakpoint !== currentBreakpoint) {
        currentBreakpoint = newBreakpoint;
        callback(currentBreakpoint);
      }
    };
    
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }
};

/**
 * CSS Utilities for dynamic styling
 */
const cssUtils = {
  /**
   * Add a CSS class dynamically
   * @param {string} className - Class name
   * @param {Object} rules - CSS rules
   */
  createClass(className, rules) {
    if (typeof document === 'undefined') return;
    
    const style = document.createElement('style');
    style.type = 'text/css';
    document.head.appendChild(style);
    
    const formattedRules = Object.entries(rules)
      .map(([prop, value]) => {
        // Convert camelCase to kebab-case
        const cssProperty = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
        return `${cssProperty}: ${value};`;
      })
      .join(' ');
    
    style.sheet.insertRule(`.${className} { ${formattedRules} }`, 0);
  },
  
  /**
   * Apply CSS variables to an element or :root
   * @param {Object} variables - CSS variables
   * @param {Element} element - Target element (defaults to :root)
   */
  setCssVariables(variables, element = document.documentElement) {
    Object.entries(variables).forEach(([name, value]) => {
      const cssVarName = name.startsWith('--') ? name : `--${name}`;
      element.style.setProperty(cssVarName, value);
    });
  },
  
  /**
   * Generate responsive CSS for different breakpoints
   * @param {Object} breakpoints - CSS by breakpoint
   * @returns {string} - Media query CSS
   */
  responsiveCss(breakpoints) {
    const breakpointMap = {
      xs: '(max-width: 575.98px)',
      sm: '(min-width: 576px) and (max-width: 767.98px)',
      md: '(min-width: 768px) and (max-width: 991.98px)',
      lg: '(min-width: 992px) and (max-width: 1199.98px)',
      xl: '(min-width: 1200px)'
    };
    
    let css = '';
    
    Object.entries(breakpoints).forEach(([breakpoint, styles]) => {
      const mediaQuery = breakpointMap[breakpoint];
      if (mediaQuery) {
        css += `@media ${mediaQuery} {\n`;
        
        Object.entries(styles).forEach(([selector, rules]) => {
          css += `  ${selector} {\n`;
          
          Object.entries(rules).forEach(([prop, value]) => {
            // Convert camelCase to kebab-case
            const cssProperty = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
            css += `    ${cssProperty}: ${value};\n`;
          });
          
          css += '  }\n';
        });
        
        css += '}\n';
      }
    });
    
    return css;
  }
};

// Export all services
export {
  httpService,
  sqlService,
  noSqlService,
  jQueryBridge,
  backendServices,
  responsiveUtils,
  cssUtils
};

// Default export
export default {
  http: httpService,
  sql: sqlService,
  nosql: noSqlService,
  jquery: jQueryBridge,
  backend: backendServices,
  responsive: responsiveUtils,
  css: cssUtils
};
