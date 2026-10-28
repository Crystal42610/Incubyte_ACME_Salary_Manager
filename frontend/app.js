/* ACME Salary Manager: React 19 client, bundled locally with esbuild. */
import React from 'react';
import { createRoot } from 'react-dom/client';
(function () {
  'use strict';
  const h = React.createElement;
  const PERIOD = 'Annual base salary';
  const E = (tag, props, ...children) => h(tag, props || {}, ...children);
  const cx = (...classes) => classes.filter(Boolean).join(' ');

  function money(amount, currency) {
    if (amount == null) return '—';
    try { return new Intl.NumberFormat('en-US', { style: 'currency', currency, maximumFractionDigits: 2 }).format(Number(amount)); }
    catch (_) { return amount + ' ' + currency; }
  }
  function dateTime(iso) { return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }); }
  function initials(fullName) { return fullName.split(' ').slice(0, 2).map(s => s.charAt(0)).join('').toUpperCase(); }
  function option(value, text) { return E('option', { key: value, value }, text); }
  function pill(text, kind) { return E('span', { className: cx('pill', kind || 'neutral') }, text); }
  function metric(title, value, note) {
    return E('div', { className: 'metric-card', key: title },
      E('span', { className: 'metric-label' }, title), E('strong', { className: 'metric-number' }, value),
      E('span', { className: 'metric-note' }, note));
  }
  function emptyState(message) { return E('div', { className: 'empty-state' }, E('div', { className: 'empty-icon' }, '⌕'), E('p', {}, message)); }

  class SalaryApp extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        user: '', password: '', authorization: '', view: 'directory',
        meta: null, rows: [], total: 0, page: 1, pageSize: 20, search: '', country: '', department: '', sort: 'employee_code',
        currency: 'EUR', stats: null, selected: null, history: [], editedSalary: '', editReason: '',
        busy: false, saving: false, alert: '', message: ''
      };
      this.requestCounter = 0;
    }
    async request(path, options) {
      const opts = options || {};
      const response = await fetch('/api' + path, {
        method: opts.method || 'GET',
        headers: { 'Authorization': this.state.authorization, 'Content-Type': 'application/json' },
        body: opts.body == null ? undefined : JSON.stringify(opts.body),
        cache: 'no-store'
      });
      let data = {};
      try { data = await response.json(); } catch (_) { /* fallback below */ }
      if (!response.ok) {
        const detail = Array.isArray(data.detail) ? data.detail.map(x => x.msg).join('; ') : data.detail;
        const failure = new Error(detail || ('Request failed (' + response.status + ')'));
        failure.status = response.status;
        throw failure;
      }
      return data;
    }
    setFailure(error) {
      this.setState({ alert: error.message || 'An unexpected error occurred.', busy: false, saving: false });
    }
    async login(event) {
      event.preventDefault();
      this.setState({ busy: true, alert: '' });
      const authorization = 'Basic ' + btoa(String.fromCharCode(...new TextEncoder().encode(this.state.user + ':' + this.state.password)));
      try {
        const response = await fetch('/api/me', { headers: { Authorization: authorization }, cache: 'no-store' });
        if (!response.ok) throw new Error(response.status === 503 ? 'HR credentials are not configured on the server.' : 'Unable to sign in. Check your HR credentials.');
        this.setState({ authorization, password: '', busy: false }, () => {
          this.loadMeta(); this.loadDirectory(); this.loadAnalytics();
        });
      } catch (error) { this.setFailure(error); }
    }
    signOut() {
      this.requestCounter++;
      this.setState({ authorization: '', user: '', password: '', view: 'directory', selected: null, history: [], rows: [], stats: null, meta: null, total: 0, page: 1, search: '', country: '', department: '', sort: 'employee_code', currency: 'EUR', alert: '', message: '' });
    }
    async loadMeta() {
      try { this.setState({ meta: await this.request('/meta') }); }
      catch (e) { this.setFailure(e); }
    }
    async loadDirectory() {
      const requestId = ++this.requestCounter;
      const { search, country, department, page, pageSize, sort } = this.state;
      const params = new URLSearchParams({ q: search, country, department, page: String(page), page_size: String(pageSize), sort });
      this.setState({ busy: true, alert: '' });
      try {
        const data = await this.request('/employees?' + params.toString());
        if (requestId === this.requestCounter) this.setState({ rows: data.items, total: data.total, busy: false });
      } catch (e) { if (requestId === this.requestCounter) this.setFailure(e); }
    }
    async loadAnalytics() {
      try { this.setState({ stats: await this.request('/analytics?currency=' + encodeURIComponent(this.state.currency)) }); }
      catch (e) { this.setFailure(e); }
    }
    updateFilter(key, value) {
      this.setState({ [key]: value, page: 1 }, () => this.loadDirectory());
    }
    changeView(view) {
      this.setState({ view, alert: '', message: '' }, () => (view === 'insights' ? this.loadAnalytics() : this.loadDirectory()));
    }
    async openEmployee(id) {
      this.setState({ alert: '' });
      try {
        const [selected, history] = await Promise.all([
          this.request('/employees/' + id), this.request('/employees/' + id + '/history')
        ]);
        this.setState({ selected, history, editedSalary: selected.salary, editReason: '', alert: '' });
      } catch (e) { this.setFailure(e); }
    }
    async saveSalary(event) {
      event.preventDefault();
      const { selected, editedSalary, editReason } = this.state;
      this.setState({ saving: true, alert: '', message: '' });
      try {
        const saved = await this.request('/employees/' + selected.id + '/salary', {
          method: 'PATCH',
          body: { salary: editedSalary, reason: editReason, expected_version: selected.version }
        });
        const history = await this.request('/employees/' + saved.id + '/history');
        this.setState({ selected: saved, editedSalary: saved.salary, editReason: '', history,
          saving: false, message: 'Salary saved and audit trail updated.' });
        this.loadDirectory();
        this.loadAnalytics();
      } catch (e) {
        if (e.status === 409) {
          this.setFailure(e);
        } else this.setFailure(e);
      }
    }
    async refreshSelected() {
      if (this.state.selected) await this.openEmployee(this.state.selected.id);
    }
    loginScreen() {
      return E('div', { className: 'login-shell' },
        E('div', { className: 'login-decoration' },
          E('div', { className: 'brand-mark large' }, 'A'),
          E('div', { className: 'login-story' }, E('span', { className: 'eyebrow light' }, 'A smarter HR workspace'),
            E('h1', {}, 'Clarity in every compensation decision.'),
            E('p', {}, 'Find people faster, maintain accurate salaries and turn scattered spreadsheets into useful insights.')),
          E('div', { className: 'login-footer' }, 'ACME  /  INTERNAL HR SYSTEM')),
        E('div', { className: 'login-panel' }, E('div', { className: 'login-form-wrap' },
          E('div', { className: 'tiny-label' }, 'SECURE HR PORTAL'),
          E('h2', {}, 'Welcome back'),
          E('p', { className: 'muted' }, 'Sign in with your administrator credentials to access the salary workspace.'),
          this.state.alert ? E('div', { className: 'alert error', role: 'alert' }, this.state.alert) : null,
          E('form', { onSubmit: e => this.login(e) },
            E('label', { htmlFor: 'username' }, 'Username'),
            E('input', { id: 'username', autoComplete: 'username', required: true, placeholder: 'hr-admin', value: this.state.user, onChange: e => this.setState({ user: e.target.value }) }),
            E('label', { htmlFor: 'password' }, 'Password'),
            E('input', { id: 'password', type: 'password', autoComplete: 'current-password', required: true, placeholder: '••••••••••', value: this.state.password, onChange: e => this.setState({ password: e.target.value }) }),
            E('button', { className: 'primary full', type: 'submit', disabled: this.state.busy }, this.state.busy ? 'Signing in…' : 'Sign in to dashboard  →')),
          E('p', { className: 'login-disclaimer' }, 'Demo environment · Synthetic employee records only'))));
    }
    header() {
      return E('header', { className: 'header' },
        E('div', { className: 'header-inner' },
          E('div', { className: 'brand' }, E('div', { className: 'brand-mark' }, 'A'), E('div', {}, E('strong', {}, 'ACME'), E('span', {}, 'Salary Manager'))),
          E('nav', { className: 'tabs', 'aria-label': 'Main navigation' },
            E('button', { className: cx('tab', this.state.view === 'directory' && 'active'), onClick: () => this.changeView('directory') }, 'Employee directory'),
            E('button', { className: cx('tab', this.state.view === 'insights' && 'active'), onClick: () => this.changeView('insights') }, 'Pay insights')),
          E('div', { className: 'profile' }, E('div', { className: 'avatar-small' }, 'HR'), E('div', { className: 'profile-text' }, E('b', {}, this.state.user), E('small', {}, 'HR Manager')),
            E('button', { className: 'text-button', onClick: () => this.signOut(), title: 'Sign out' }, 'Sign out'))));
    }
    directoryView() {
      const { meta, rows, total, page, pageSize, search, country, department, sort } = this.state;
      const pages = Math.max(1, Math.ceil(total / pageSize));
      return E('section', {},
        E('div', { className: 'page-heading' }, E('div', {}, E('span', { className: 'eyebrow' }, 'PEOPLE & COMPENSATION'),
          E('h1', {}, 'Employee directory'), E('p', {}, 'Find, review and manage compensation with an auditable record of every change.')),
          E('div', { className: 'total-count' }, E('b', {}, meta ? meta.total.toLocaleString() : '—'), E('span', {}, 'Employees in workspace'))),
        E('div', { className: 'table-card' },
          E('div', { className: 'card-top' },
            E('div', { className: 'card-title' }, E('h2', {}, 'All employees'), E('p', {}, total.toLocaleString() + ' matching records')),
            pill('Live directory', 'mint')),
          E('div', { className: 'filter-row' },
            E('div', { className: 'search-box' }, E('span', { 'aria-hidden': true }, '⌕'),
              E('input', { 'aria-label': 'Search by name, employee code or email', placeholder: 'Search name, code or email…', value: search,
                onChange: e => this.updateFilter('search', e.target.value) })),
            E('label', { className: 'select-wrap' }, E('span', {}, 'Country'),
              E('select', { value: country, onChange: e => this.updateFilter('country', e.target.value) }, option('', 'All countries'), ...(meta ? meta.countries.map(c => option(c,c)) : []))),
            E('label', { className: 'select-wrap' }, E('span', {}, 'Department'),
              E('select', { value: department, onChange: e => this.updateFilter('department', e.target.value) }, option('', 'All departments'), ...(meta ? meta.departments.map(d => option(d,d)) : []))),
            E('label', { className: 'select-wrap small' }, E('span', {}, 'Sort by'),
              E('select', { value: sort, onChange: e => this.updateFilter('sort', e.target.value) },
                option('employee_code','Employee ID'), option('full_name','Name'), option('salary','Salary'),option('department','Department')))),
          E('div', { className: 'table-scroll' }, E('table', { className: 'data-table' },
            E('thead', {}, E('tr', {}, E('th', {}, 'EMPLOYEE'), E('th', {}, 'DEPARTMENT'), E('th', {}, 'COUNTRY'), E('th', {}, PERIOD.toUpperCase()), E('th', {}, 'DETAILS'))),
            E('tbody', {}, rows.map(item => E('tr', { key: item.id },
              E('td', {}, E('div', { className: 'employee-cell' }, E('div', { className: 'avatar' }, initials(item.full_name)),
                E('div', {}, E('strong', {}, item.full_name), E('small', {}, item.employee_code + ' · ' + item.email)))),
              E('td', {}, E('span', { className: 'department-tag' }, item.department)),
              E('td', {}, item.country_code),
              E('td', { className: 'number-cell' }, money(item.salary, item.currency), E('small', {}, item.currency)),
              E('td', {}, E('button', { className: 'link-button', onClick: () => this.openEmployee(item.id) }, 'View / edit  →'))))),
            !rows.length ? E('tbody', {}, E('tr', {}, E('td', { colSpan: 5 }, emptyState(this.state.busy ? 'Loading employees…' : 'No employees match these filters.')))) : null)),
          E('div', { className: 'pagination' }, E('span', {}, 'Showing ' + (total ? (page-1)*pageSize+1 : 0) + '–' + Math.min(page*pageSize,total) + ' of ' + total.toLocaleString()),
            E('div', { className: 'pagination-actions' },
              E('button', { disabled: page <= 1, onClick: () => this.setState({page:page-1},()=>this.loadDirectory()) }, '← Previous'),
              E('span', {}, page + ' / ' + pages),
              E('button', { disabled: page >= pages, onClick: () => this.setState({page:page+1},()=>this.loadDirectory()) }, 'Next →')))));
    }
    breakdown(title, items, currency) {
      const highest = Math.max(1, ...items.map(x => x.headcount));
      return E('section', { className: 'breakdown-card' }, E('h2', {}, title), E('p', { className: 'muted' }, 'Headcount and average annual base salary'),
        E('div', { className: 'breakdown-list' }, items.map((item, idx) => E('div', { className: 'bar-row', key: item.label },
          E('div', { className: 'bar-row-heading' }, E('strong', {}, item.label), E('span', {}, money(item.average, currency))),
          E('div', { className: 'bar-track' }, E('div', { className: cx('bar-fill', idx % 2 ? 'alt' : ''), style: { width: (item.headcount / highest * 100) + '%' } })),
          E('div', { className: 'bar-row-foot' }, item.headcount.toLocaleString() + ' employees')))));
    }
    insightsView() {
      const { stats, currency, meta } = this.state;
      return E('section', {},
        E('div', { className: 'page-heading' }, E('div', {}, E('span', { className: 'eyebrow' }, 'COMPENSATION INTELLIGENCE'),
          E('h1', {}, 'Pay insights'), E('p', {}, 'Understand pay patterns without mixing currencies or compromising accuracy.')),
          E('label', { className: 'currency-control' }, E('span', {}, 'REPORTING CURRENCY'),
            E('select', { value: currency, onChange: e => this.setState({ currency:e.target.value, stats:null },()=>this.loadAnalytics()) },
              ...(meta ? meta.currencies.map(c => option(c,c)) : [option('EUR','EUR')])))),
        E('div', { className: 'notice' }, E('b', {}, 'Currency-safe reporting.'), ' These figures include only employees paid in ' + currency + '. No exchange rates or mixed-currency totals are assumed.'),
        !stats ? E('p', { role: 'status', className: 'muted' }, 'Loading compensation analytics…') :
          E('div', {}, E('div', { className: 'metrics-grid' },
            metric('Employees in ' + currency, stats.headcount.toLocaleString(), 'Current active records'),
            metric('Average salary', money(stats.average,currency), PERIOD),
            metric('Median salary', money(stats.median,currency), PERIOD),
            metric('Salary range', money(stats.minimum,currency) + ' — ' + money(stats.maximum,currency), 'Minimum to maximum')),
            E('div', { className: 'two-columns' },
              this.breakdown('By department',stats.by_department,currency),
              this.breakdown('By country',stats.by_country,currency))));
    }
    employeeModal() {
      const { selected, editedSalary, editReason, history } = this.state;
      if (!selected) return null;
      return E('div', { className: 'modal-backdrop', role: 'presentation', onClick: e => { if(e.target === e.currentTarget) this.setState({ selected: null, alert:'', message:'' }); } },
        E('section', { className: 'modal', role: 'dialog', 'aria-modal': true, 'aria-labelledby': 'detail-heading' },
          E('div', { className: 'modal-header' }, E('div', {}, E('span', { className: 'eyebrow' }, 'COMPENSATION RECORD'),
            E('h2', { id: 'detail-heading' }, selected.full_name), E('p', {}, selected.employee_code + ' · ' + selected.department + ' · ' + selected.country_code)),
            E('button', { className: 'modal-close', onClick: () => this.setState({ selected:null, alert:'', message:'' }), 'aria-label':'Close details' }, '×')),
          E('div', { className: 'modal-scroll' },
            E('div', { className:'current-salary' }, E('span', {}, 'CURRENT ANNUAL BASE SALARY'), E('strong', {}, money(selected.salary,selected.currency)),
              E('small', {}, 'Currency ' + selected.currency + ' · Record version ' + selected.version)),
            E('h3', {}, 'Update compensation'),
            E('p', { className:'muted' }, 'All changes are recorded with a reason and timestamp.'),
            this.state.alert ? E('div', { className: 'alert error', role: 'alert' }, this.state.alert, ' ',
              E('button', { onClick: () => this.refreshSelected(), className:'link-button' }, 'Refresh employee')) : null,
            this.state.message ? E('div', { className: 'alert success', role: 'status' }, this.state.message) : null,
            E('form', { className: 'salary-form', onSubmit: e=>this.saveSalary(e) },
              E('label', { htmlFor: 'new-salary' }, 'New annual salary (' + selected.currency + ')'),
              E('input', { id:'new-salary', inputMode: 'decimal', required:true, pattern:'[0-9]{1,12}(\\.[0-9]{1,2})?', value: editedSalary,
                onChange:e=>this.setState({editedSalary:e.target.value}), placeholder:'e.g. 78000.00' }),
              E('label', { htmlFor:'reason' }, 'Reason for change'),
              E('textarea', { id:'reason', rows:2, required:true, minLength:5, maxLength:240,
                value:editReason, onChange:e=>this.setState({editReason:e.target.value}), placeholder:'e.g. Annual compensation review approved by HR' }),
              E('button', { type:'submit', className:'primary', disabled:this.state.saving }, this.state.saving ? 'Saving…' : 'Save salary change')),
            E('div', { className: 'history-header' }, E('h3', {}, 'Change history'), pill(history.length + (history.length === 1 ? ' change' : ' changes'), 'neutral')),
            !history.length ? E('p', { className:'muted' }, 'No salary changes have been recorded yet.') :
              E('div', { className:'history-list' }, history.map(record => E('div', { className:'history-event', key:record.id },
                E('div', { className:'history-dot' }), E('div', {},
                  E('strong', {}, money(record.old_salary,record.currency) + ' → ' + money(record.new_salary,record.currency)),
                  E('span', {}, record.reason), E('small', {}, dateTime(record.changed_at) + ' · ' + record.changed_by))))))));
    }
    render() {
      if (!this.state.authorization) return this.loginScreen();
      return E('div', { className:'app-shell' }, this.header(),
        E('main', { className:'main-content' },
          this.state.alert && !this.state.selected ? E('div', { className:'alert error', role:'alert' }, this.state.alert) : null,
          this.state.view === 'directory' ? this.directoryView() : this.insightsView()),
        E('footer', { className:'site-footer' }, E('span', {}, 'ACME / Salary Manager'), E('span', {}, 'Demo uses synthetic employee data · All times UTC in audit records')),
        this.employeeModal());
    }
  }
  createRoot(document.getElementById('root')).render(E(SalaryApp));
}());
