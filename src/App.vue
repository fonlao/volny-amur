<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

const menuOpen = ref(false)
const activeRoute = ref(0)
const activeMapRoute = ref(0)
const activeFaq = ref(0)
const mapElement = ref(null)
const mapMessage = ref('')
const departures = ref([])
const activeCalendarMonth = ref('all')
const departuresLoading = ref(true)
const theme = ref('light')
const accountOpen = ref(false)
const accountMode = ref('login')
const accountLoading = ref(false)
const accountError = ref('')
const account = ref({ authenticated: false, user: null, leads: [], payments: [] })
const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ name: '', email: '', phone: '', password: '' })
const sending = ref(false)
const status = ref('')
const paymentLoading = ref(false)
const paymentStatus = ref('')
const form = ref({ name: '', phone: '', email: '', route: 'Шантарские острова', departure_id: '', departure_label: '' })
const site = ref({
  hero_eyebrow: 'Хабаровский край · Дальний Восток', hero_title: 'Там, где начинается настоящее',
  hero_text: 'Авторские путешествия в места, где тайга встречается с океаном, а каждый день становится историей.',
  advantages_title: 'Дальше — только настоящее', routes_title: 'Выберите своё направление',
  guides_title: 'Люди, которым доверяют путь', request_title: 'Ваше приключение начинается здесь',
  request_text: 'Оставьте контакты — наш эксперт позвонит и поможет выбрать идеальный маршрут.',
  email: 'hello@volniyamur.ru', phone: '+7 4212 99-00-48', booking_deposit: '5000.00'
})

const advantages = ref([
  { icon: '⌖', title: 'Знаем каждый поворот', text: 'Живём на Дальнем Востоке и ходим этими тропами больше 12 лет.' },
  { icon: '♢', title: 'Маленькие группы', text: 'До 8 человек — чтобы слышать тайгу, а не шум туристической толпы.' },
  { icon: '⊕', title: 'Безопасность в деталях', text: 'Спутниковая связь, проверенное снаряжение и сертифицированные гиды.' },
  { icon: '≈', title: 'Бережно к природе', text: 'Следуем принципу «не оставляй следов» и поддерживаем заповедники края.' }
])

const routes = ref([
  { number: '01', title: 'Шантарские острова', tag: 'Экспедиция', days: '8 дней', level: 'Средний', price: 'от 168 000 ₽', season: 'июль — сентябрь', text: 'Киты в Охотском море, лежбища тюленей и дикие бухты архипелага. Добираемся катером и живём в тёплом глэмпинге.', art: 'ocean', start_location: 'Комсомольск-на-Амуре', start_latitude: 50.549923, start_longitude: 137.007948 },
  { number: '02', title: 'Дуссе-Алинь', tag: 'Треккинг', days: '10 дней', level: 'Сложный', price: 'от 124 000 ₽', season: 'июнь — август', text: 'Горные озёра, водопады и каменные цирки заповедного хребта. Настоящая автономная экспедиция с опытным проводником.', art: 'mountain', start_location: 'Посёлок Бриакан', start_latitude: 50.711744, start_longitude: 134.066509 },
  { number: '03', title: 'По следам тигра', tag: 'Экотур', days: '5 дней', level: 'Лёгкий', price: 'от 76 000 ₽', season: 'февраль — март', text: 'Зимняя тайга Сихотэ-Алиня, следы амурского тигра и ночёвки на кордоне. Наблюдаем природу бережно и с безопасной дистанции.', art: 'forest', start_location: 'Хабаровск', start_latitude: 48.480223, start_longitude: 135.071917 },
  { number: '04', title: 'Амурские протоки', tag: 'Сплав', days: '4 дня', level: 'Лёгкий', price: 'от 49 000 ₽', season: 'май — октябрь', text: 'Неторопливое путешествие на каяках среди островов великой реки, рыбацких сёл и дальневосточных закатов.', art: 'river', start_location: 'Хабаровск, набережная Амура', start_latitude: 48.472607, start_longitude: 135.052664 }
])

const guides = ref([
  { name: 'Артём Волков', role: 'Экспедиционный гид', exp: '12 лет в тайге', quote: 'Знает Шантары как свой дом', initials: 'АВ', color: 'green' },
  { name: 'Лидия Ким', role: 'Гид-натуралист', exp: 'Кандидат биологических наук', quote: 'Переводит язык дикой природы', initials: 'ЛК', color: 'blue' },
  { name: 'Михаил Серов', role: 'Горный проводник', exp: '38 восхождений', quote: 'В горах выбирает верный темп', initials: 'МС', color: 'dark' }
])

const reviews = [
  { name: 'Елена Орлова', city: 'Москва', route: 'Шантарские острова', date: 'Сентябрь 2025', text: 'Это была не просто поездка, а настоящая экспедиция. Киты подошли так близко, что мы забыли про камеры. Всё продумано до мелочей.', initials: 'ЕО', color: 'lime' },
  { name: 'Илья Кузнецов', city: 'Хабаровск', route: 'Амурские протоки', date: 'Июль 2025', text: 'Идеальный формат для перезагрузки на выходных. Спокойная вода, красивые стоянки и гид, который знает каждую протоку.', initials: 'ИК', color: 'sky' },
  { name: 'Марина Белова', city: 'Санкт-Петербург', route: 'Дуссе-Алинь', date: 'Август 2024', text: 'Сложный маршрут, который оказался по силам всей нашей группе. Спасибо за темп, заботу и чувство настоящего приключения.', initials: 'МБ', color: 'forest' },
  { name: 'Александр Руденко', city: 'Владивосток', route: 'По следам тигра', date: 'Март 2025', text: 'Увидели следы тигра и услышали тайгу зимой. Вернулся домой с ощущением, что побывал в другом мире.', initials: 'АР', color: 'ink' }
]

const faqs = [
  { question: 'Что входит в стоимость путешествия?', answer: 'Трансферы по программе, проживание, питание на маршруте, работа специалистов, групповое снаряжение и средства спутниковой связи. Перелёт до Хабаровска оплачивается отдельно.' },
  { question: 'Нужна ли специальная физическая подготовка?', answer: 'Для каждого маршрута указан уровень сложности. Для лёгких программ достаточно обычной активности, а перед сложным треккингом специалист уточнит ваш опыт и поможет подготовиться.' },
  { question: 'Что делать, если изменится погода?', answer: 'На Дальнем Востоке погода переменчива, поэтому в каждой программе предусмотрен резерв времени. Руководитель группы может безопасно скорректировать порядок или продолжительность этапов.' },
  { question: 'Можно ли путешествовать с детьми?', answer: 'Да, для семей подходят маршруты лёгкого уровня. Возраст ребёнка и формат поездки лучше заранее обсудить со специалистом — мы предложим комфортную программу.' },
  { question: 'Как забронировать место?', answer: 'Оставьте заявку на сайте. Мы свяжемся с вами, ответим на вопросы, подтвердим доступные даты и отправим договор с условиями бронирования.' }
]

let routeMap = null
const routeMarkers = new Map()
let yandexMapsPromise = null

function mappedRoutes() {
  return routes.value
    .map((route, index) => ({
      route,
      index,
      lat: Number(route.start_latitude),
      lng: Number(route.start_longitude)
    }))
    .filter(item => Number.isFinite(item.lat) && Number.isFinite(item.lng))
}

function loadYandexMaps(apiKey) {
  if (window.ymaps) return Promise.resolve(window.ymaps)
  if (yandexMapsPromise) return yandexMapsPromise
  yandexMapsPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${encodeURIComponent(apiKey)}&lang=ru_RU`
    script.async = true
    script.onload = () => window.ymaps.ready(() => resolve(window.ymaps))
    script.onerror = () => reject(new Error('Не удалось загрузить Яндекс Карты'))
    document.head.appendChild(script)
  })
  return yandexMapsPromise
}

async function initRouteMap() {
  if (!mapElement.value) return
  if (routeMap) routeMap.destroy()
  routeMarkers.clear()
  const points = mappedRoutes()
  if (!points.length) return
  if (!site.value.yandex_maps_api_key) {
    mapMessage.value = 'Для отображения карты добавьте API-ключ Яндекс.Карт в общих настройках сайта.'
    return
  }
  try {
    const ymaps = await loadYandexMaps(site.value.yandex_maps_api_key)
    mapMessage.value = ''
    routeMap = new ymaps.Map(mapElement.value, {
      center: [49.4, 135.4],
      zoom: 6,
      controls: ['zoomControl', 'fullscreenControl']
    })
    routeMap.behaviors.disable('scrollZoom')
    points.forEach(({ route, index, lat, lng }) => {
      const marker = new ymaps.Placemark([lat, lng], {
        iconContent: String(index + 1).padStart(2, '0'),
        balloonContentHeader: route.title,
        balloonContentBody: `Старт: ${route.start_location || 'точка указана на карте'}`,
        hintContent: route.title
      }, {
        preset: 'islands#darkGreenStretchyIcon'
      })
      marker.events.add('click', () => { activeMapRoute.value = index })
      routeMap.geoObjects.add(marker)
      routeMarkers.set(index, marker)
    })
    routeMap.setBounds(routeMap.geoObjects.getBounds(), { checkZoomRange: true, zoomMargin: 55 })
  } catch (error) {
    mapMessage.value = error.message
  }
}

function focusMapRoute(index) {
  const item = mappedRoutes().find(point => point.index === index)
  const marker = routeMarkers.get(index)
  if (!item || !routeMap || !marker) return
  activeMapRoute.value = index
  routeMap.setCenter([item.lat, item.lng], Math.max(routeMap.getZoom(), 7), { duration: 500 })
  marker.balloon.open()
}

function openRouteFromMap(index) {
  activeRoute.value = index
  scrollTo('routes')
}

const monthFormatter = new Intl.DateTimeFormat('ru-RU', { month: 'long', year: 'numeric' })
const dateFormatter = new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'short' })

function departureMonthKey(departure) {
  return departure.start_date.slice(0, 7)
}

function calendarMonths() {
  const unique = [...new Set(departures.value.map(departureMonthKey))]
  return unique.map(value => ({
    value,
    label: monthFormatter.format(new Date(`${value}-01T12:00:00`))
  }))
}

function visibleDepartures() {
  return activeCalendarMonth.value === 'all'
    ? departures.value
    : departures.value.filter(item => departureMonthKey(item) === activeCalendarMonth.value)
}

function departureStatus(departure) {
  if (departure.status === 'closed') return { label: 'Набор закрыт', className: 'closed' }
  if (departure.status === 'waitlist') return { label: 'Лист ожидания', className: 'waitlist' }
  if (departure.status === 'few' || departure.available_places <= 2) return { label: `Осталось ${departure.available_places}`, className: 'few' }
  return { label: `${departure.available_places} мест`, className: 'open' }
}

function formatDepartureRange(departure) {
  const start = new Date(`${departure.start_date}T12:00:00`)
  const end = new Date(`${departure.end_date}T12:00:00`)
  return `${dateFormatter.format(start)} — ${dateFormatter.format(end)}`
}

function selectDeparture(departure) {
  if (departure.status === 'closed') return
  form.value.route = departure.route
  form.value.departure_id = departure.id
  form.value.departure_label = formatDepartureRange(departure)
  scrollTo('request')
}

function splitTitle(text) {
  const words = (text || '').trim().split(/\s+/)
  const cut = Math.max(1, words.length - 2)
  return { lead: words.slice(0, cut).join(' '), accent: words.slice(cut).join(' ') }
}

function applyTheme(nextTheme) {
  theme.value = nextTheme
  localStorage.setItem('volny-amur-theme', nextTheme)
  document.documentElement.dataset.theme = nextTheme
}

function toggleTheme() {
  applyTheme(theme.value === 'dark' ? 'light' : 'dark')
}

function initTheme() {
  const saved = localStorage.getItem('volny-amur-theme')
  const preferred = window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  applyTheme(saved === 'dark' || saved === 'light' ? saved : preferred)
}

initTheme()

function getCookie(name) {
  const item = document.cookie.split('; ').find(row => row.startsWith(`${name}=`))
  return item ? decodeURIComponent(item.split('=').slice(1).join('=')) : ''
}

async function ensureCsrf() {
  await fetch('/api/auth/csrf', { credentials: 'same-origin' })
  return getCookie('csrftoken')
}

async function accountPost(url, payload = {}) {
  const csrfToken = await ensureCsrf()
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
    body: JSON.stringify(payload)
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.message || 'Не удалось выполнить действие')
  return data
}

function applyAccountToRequest() {
  if (!account.value.user) return
  form.value.name = account.value.user.name || form.value.name
  form.value.email = account.value.user.email || form.value.email
  form.value.phone = account.value.user.phone || form.value.phone
}

async function loadAccount() {
  try {
    const response = await fetch('/api/auth/me', { credentials: 'same-origin' })
    const data = await response.json()
    account.value = data.authenticated
      ? { authenticated: true, user: data.user, leads: data.leads || [], payments: data.payments || [] }
      : { authenticated: false, user: null, leads: [], payments: [] }
    applyAccountToRequest()
  } catch (_) {
    account.value = { authenticated: false, user: null, leads: [], payments: [] }
  }
}

async function openAccount(mode = 'login') {
  accountMode.value = mode
  accountError.value = ''
  accountOpen.value = true
  document.body.classList.add('modal-open')
  await loadAccount()
}

function closeAccount() {
  accountOpen.value = false
  accountError.value = ''
  document.body.classList.remove('modal-open')
}

async function submitLogin() {
  accountLoading.value = true
  accountError.value = ''
  try {
    await accountPost('/api/auth/login', loginForm.value)
    loginForm.value.password = ''
    await loadAccount()
  } catch (error) {
    accountError.value = error.message
  } finally {
    accountLoading.value = false
  }
}

async function submitRegistration() {
  accountLoading.value = true
  accountError.value = ''
  try {
    await accountPost('/api/auth/register', registerForm.value)
    registerForm.value.password = ''
    await loadAccount()
  } catch (error) {
    accountError.value = error.message
  } finally {
    accountLoading.value = false
  }
}

async function logoutAccount() {
  accountLoading.value = true
  try {
    await accountPost('/api/auth/logout')
    account.value = { authenticated: false, user: null, leads: [], payments: [] }
    accountMode.value = 'login'
  } catch (error) {
    accountError.value = error.message
  } finally {
    accountLoading.value = false
  }
}

onMounted(async () => {
  try {
    const [contentResponse, departuresResponse] = await Promise.all([
      fetch('/api/content'),
      fetch('/api/departures')
    ])
    if (!contentResponse.ok) return
    const data = await contentResponse.json()
    site.value = data.site
    if (data.advantages?.length) advantages.value = data.advantages
    if (data.routes?.length) {
      routes.value = data.routes.map((item, index) => ({ ...item, number: String(index + 1).padStart(2, '0'), art: item.visual_style }))
      form.value.route = routes.value[0].title
    }
    if (data.guides?.length) guides.value = data.guides.map(item => ({ ...item, exp: item.experience }))
    if (departuresResponse.ok) {
      const departuresData = await departuresResponse.json()
      departures.value = departuresData.departures || []
    }
  } catch (_) {
    // Встроенное содержимое остаётся доступным, если API временно недоступен.
  } finally {
    departuresLoading.value = false
    await nextTick()
    initRouteMap()
  }
})

onBeforeUnmount(() => {
  if (routeMap) routeMap.destroy()
})

function scrollTo(id) {
  menuOpen.value = false
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function chooseRoute(name) {
  form.value.route = name
  scrollTo('request')
}

async function submitForm() {
  status.value = ''
  sending.value = true
  try {
    const response = await fetch('/api/requests', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form.value) })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Не удалось отправить заявку')
    status.value = 'Спасибо! Мы свяжемся с вами и обсудим детали путешествия.'
    form.value.name = ''
    form.value.phone = ''
  } catch (error) {
    status.value = error.message
  } finally {
    sending.value = false
  }
}

async function startPayment(event) {
  if (!event.currentTarget.form.reportValidity()) return
  paymentStatus.value = ''
  paymentLoading.value = true
  try {
    const response = await fetch('/api/payments/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Не удалось создать платёж')
    window.location.href = data.confirmation_url
  } catch (error) {
    paymentStatus.value = error.message
  } finally {
    paymentLoading.value = false
  }
}

async function checkPayment() {
  const paymentId = new URLSearchParams(window.location.search).get('payment')
  if (!paymentId) return
  try {
    const response = await fetch(`/api/payments/status/${paymentId}`)
    const data = await response.json()
    paymentStatus.value = data.paid
      ? `Оплата предоплаты за «${data.route}» прошла успешно.`
      : `Платёж за «${data.route}» пока имеет статус: ${data.status}.`
    window.history.replaceState({}, '', window.location.pathname + window.location.hash)
    setTimeout(() => scrollTo('request'), 100)
  } catch (_) {
    paymentStatus.value = 'Не удалось проверить статус платежа. Откройте раздел «Платежи ЮKassa» в админке.'
  }
}

onMounted(checkPayment)
onMounted(loadAccount)
</script>

<template>
  <div class="site-shell">
    <header class="header">
      <a class="logo" href="#top" aria-label="Вольный Амур — главная"><span class="logo-mark">⌁</span><span>ВОЛЬНЫЙ<br><b>АМУР</b></span></a>
      <nav :class="['nav', { open: menuOpen }]">
        <button @click="scrollTo('advantages')">О нас</button><button @click="scrollTo('routes')">Маршруты</button><button @click="scrollTo('guides')">Наши специалисты</button><button @click="scrollTo('reviews')">Отзывы</button>
      </nav>
      <button class="header-cta" @click="scrollTo('request')">Подобрать маршрут <span>↗</span></button>
      <button class="account-button" type="button" @click="openAccount()"><span>◎</span>{{ account.authenticated ? account.user.name : 'Личный кабинет' }}</button>
      <button class="theme-toggle" type="button" :aria-label="theme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему'" :title="theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'" @click="toggleTheme"><span>{{ theme === 'dark' ? '☀' : '☾' }}</span></button>
      <button class="menu" @click="menuOpen = !menuOpen" aria-label="Меню">{{ menuOpen ? '×' : '☰' }}</button>
    </header>

    <main>
      <section id="top" class="hero">
        <div class="hero-art" aria-hidden="true">
          <img class="figma-sun" src="/figma/hero-sun.svg" alt="">
          <img class="figma-mountains" src="/figma/hero-mountains.svg" alt="">
        </div>
        <div class="hero-grid">
          <div class="eyebrow"><span></span> {{ site.hero_eyebrow }}</div>
          <h1>{{ site.hero_title }}</h1>
          <p class="hero-copy">{{ site.hero_text }}</p>
          <button class="primary" @click="scrollTo('routes')">Исследовать маршруты <span>↗</span></button>
          <div class="hero-note"><span><b>49°</b> северной широты<br>территория свободы</span></div>
        </div>
      </section>

      <section id="advantages" class="advantages section-pad">
        <div class="section-kicker">02 / ПОЧЕМУ МЫ</div>
        <div class="section-heading"><h2>{{ splitTitle(site.advantages_title).lead }}<br><em>{{ splitTitle(site.advantages_title).accent }}</em></h2><p>Мы не продаём туры. Мы создаём экспедиции, после которых привычный мир становится немного шире.</p></div>
        <div class="adv-grid">
          <article v-for="(item, index) in advantages" :key="item.title"><span class="adv-num">{{ String(index + 1).padStart(2, '0') }}</span><div class="adv-icon">{{ item.icon }}</div><h3>{{ item.title }}</h3><p>{{ item.text }}</p></article>
        </div>
        <div class="stats"><div><b>12</b><span>лет<br>в пути</span></div><div><b>48</b><span>уникальных<br>маршрутов</span></div><div><b>1 400+</b><span>счастливых<br>путешественников</span></div><div><b>4.9</b><span>средняя<br>оценка</span></div></div>
      </section>

      <section id="routes" class="routes section-pad">
        <div class="section-kicker light">03 / МАРШРУТЫ</div>
        <div class="route-head"><h2>{{ splitTitle(site.routes_title).lead }}<br><em>{{ splitTitle(site.routes_title).accent }}</em></h2><p>От моря до гор — четыре способа увидеть Хабаровский край настоящим.</p></div>
        <div class="accordion">
          <article v-for="(route, index) in routes" :key="route.title" :class="['route-card', { active: activeRoute === index }]">
            <button class="route-summary" @click="activeRoute = activeRoute === index ? -1 : index">
              <span class="route-number">{{ route.number }}</span><span class="route-tag">{{ route.tag }}</span><strong>{{ route.title }}</strong>
              <span class="route-meta">{{ route.days }} <i>•</i> {{ route.level }}</span><span class="route-toggle">{{ activeRoute === index ? '−' : '+' }}</span>
            </button>
            <div class="route-content">
              <div :class="['route-visual', route.art, { 'has-image': route.image_url }]" :style="route.image_url ? { backgroundImage: `url(${route.image_url})` } : {}"><div class="mini-sun"></div><div class="mini-land"></div><span>ДАЛЬНИЙ ВОСТОК</span></div>
              <div class="route-info"><p>{{ route.text }}</p><dl><div><dt>Сезон</dt><dd>{{ route.season }}</dd></div><div><dt>Стоимость</dt><dd>{{ route.price }}</dd></div></dl><button @click="chooseRoute(route.title)">Хочу сюда <span>↗</span></button></div>
            </div>
          </article>
        </div>
      </section>

      <section id="route-map" class="map-section section-pad">
        <div class="section-kicker">04 / КАРТА МАРШРУТОВ</div>
        <div class="map-heading">
          <h2>Откуда начинается<br><em>ваше путешествие</em></h2>
          <p>Выберите точку на карте, чтобы увидеть место сбора и перейти к описанию маршрута.</p>
        </div>
        <div class="map-layout">
          <div class="route-map-shell">
            <div ref="mapElement" class="route-map" aria-label="Карта точек начала туристических маршрутов"></div>
            <div v-if="mapMessage" class="map-message"><strong>Яндекс Карты</strong><span>{{ mapMessage }}</span></div>
          </div>
          <div class="map-route-list">
            <article v-for="(route, index) in routes" :key="`map-${route.title}`" :class="{ active: activeMapRoute === index }">
              <button class="map-route-main" @click="focusMapRoute(index)">
                <span>{{ route.number }}</span>
                <div><strong>{{ route.title }}</strong><small>{{ route.start_location || 'Точка старта уточняется' }}</small></div>
                <i>⌖</i>
              </button>
              <button class="map-route-link" @click="openRouteFromMap(index)">О маршруте ↗</button>
            </article>
          </div>
        </div>
        <p class="map-caption">Карта предоставлена сервисом Яндекс.Карты. Точная точка встречи подтверждается специалистом перед поездкой.</p>
      </section>

      <section id="calendar" class="calendar section-pad">
        <div class="section-kicker">05 / КАЛЕНДАРЬ ЗАЕЗДОВ</div>
        <div class="calendar-heading">
          <h2>Выберите дату<br><em>будущего маршрута</em></h2>
          <p>Показываем актуальное количество свободных мест. Выберите удобный заезд — дата и маршрут автоматически появятся в заявке.</p>
        </div>
        <div v-if="calendarMonths().length" class="calendar-months" aria-label="Фильтр заездов по месяцам">
          <button :class="{ active: activeCalendarMonth === 'all' }" @click="activeCalendarMonth = 'all'">Все даты</button>
          <button v-for="month in calendarMonths()" :key="month.value" :class="{ active: activeCalendarMonth === month.value }" @click="activeCalendarMonth = month.value">{{ month.label }}</button>
        </div>
        <div v-if="departuresLoading" class="calendar-empty">Загружаем ближайшие даты…</div>
        <div v-else-if="visibleDepartures().length" class="departure-grid">
          <article v-for="departure in visibleDepartures()" :key="departure.id" :class="['departure-card', departureStatus(departure).className]">
            <div class="departure-top"><span>{{ departure.route_style }}</span><b :class="departureStatus(departure).className">{{ departureStatus(departure).label }}</b></div>
            <time :datetime="departure.start_date">{{ formatDepartureRange(departure) }}</time>
            <h3>{{ departure.route }}</h3>
            <p>{{ departure.note || 'Подробности программы уточнит наш специалист.' }}</p>
            <div class="departure-capacity"><span>Свободно</span><strong>{{ departure.available_places }} / {{ departure.capacity }}</strong><i><em :style="{ width: `${Math.max(0, Math.min(100, departure.available_places / departure.capacity * 100))}%` }"></em></i></div>
            <button :disabled="departure.status === 'closed'" @click="selectDeparture(departure)">{{ departure.status === 'waitlist' ? 'Встать в лист ожидания' : departure.status === 'closed' ? 'Набор закрыт' : 'Выбрать заезд' }} <span>↗</span></button>
          </article>
        </div>
        <div v-else class="calendar-empty">На выбранный месяц опубликованных заездов пока нет.</div>
        <div class="calendar-legend"><span><i class="open"></i> Есть места</span><span><i class="few"></i> Мало мест</span><span><i class="waitlist"></i> Лист ожидания</span></div>
      </section>

      <section id="guides" class="guides section-pad">
        <div class="section-kicker">06 / НАШИ СПЕЦИАЛИСТЫ</div>
        <div class="section-heading"><h2>{{ splitTitle(site.guides_title).lead }}<br><em>{{ splitTitle(site.guides_title).accent }}</em></h2><p>Наши гиды не просто показывают дорогу. Они помогают почувствовать место.</p></div>
        <div class="guide-grid">
          <article v-for="guide in guides" :key="guide.name">
            <div :class="['guide-photo', guide.color, { 'has-image': guide.image_url }]" :style="guide.image_url ? { backgroundImage: `url(${guide.image_url})` } : {}"><span>{{ guide.initials }}</span><div class="ridge"></div></div>
            <div class="guide-content"><small>{{ guide.role }}</small><h3>{{ guide.name }}</h3><p>«{{ guide.quote }}»</p><span class="experience">{{ guide.exp }}</span></div>
          </article>
        </div>
      </section>

      <section id="reviews" class="reviews section-pad">
        <div class="section-kicker">07 / ОТЗЫВЫ ПУТЕШЕСТВЕННИКОВ</div>
        <div class="reviews-heading">
          <div><h2>Нам доверяют<br><em>свои маршруты</em></h2><p>Истории тех, кто уже увидел Дальний Восток вместе с нами.</p></div>
          <div class="review-score" aria-label="Средняя оценка 4,9 из 5"><strong>4.9</strong><span><b>★★★★★</b><small>средняя оценка</small></span></div>
        </div>
        <div class="review-grid">
          <article v-for="review in reviews" :key="review.name" class="review-card">
            <div class="review-card-head"><div :class="['review-avatar', review.color]">{{ review.initials }}</div><div><strong>{{ review.name }}</strong><span>{{ review.city }}</span></div><b class="review-stars" aria-label="5 из 5">★★★★★</b></div>
            <p>«{{ review.text }}»</p>
            <div class="review-meta"><span>{{ review.route }}</span><time>{{ review.date }}</time></div>
          </article>
        </div>
      </section>

      <section id="faq" class="faq section-pad">
        <div class="section-kicker">08 / ВАЖНО ЗНАТЬ</div>
        <div class="faq-layout">
          <div class="faq-intro">
            <h2>Ответы на<br><em>частые вопросы</em></h2>
            <p>Собрали главное о подготовке, безопасности и бронировании путешествий.</p>
            <button class="faq-contact" @click="scrollTo('request')">Задать свой вопрос <span>↗</span></button>
          </div>
          <div class="faq-list">
            <article v-for="(item, index) in faqs" :key="item.question" :class="{ active: activeFaq === index }">
              <button :aria-expanded="activeFaq === index" @click="activeFaq = activeFaq === index ? -1 : index">
                <span>{{ String(index + 1).padStart(2, '0') }}</span>
                <strong>{{ item.question }}</strong>
                <i>{{ activeFaq === index ? '−' : '+' }}</i>
              </button>
              <div class="faq-answer"><p>{{ item.answer }}</p></div>
            </article>
          </div>
        </div>
      </section>

      <section id="request" class="request section-pad">
        <div class="request-copy"><div class="section-kicker light">09 / НАЧНЁМ?</div><h2>{{ splitTitle(site.request_title).lead }}<br><em>{{ splitTitle(site.request_title).accent }}</em></h2><p>{{ site.request_text }}</p><div class="contact-line"><span>или напишите нам</span><a :href="`mailto:${site.email}`">{{ site.email }}</a><a :href="`tel:${site.phone.replace(/[^+\d]/g, '')}`">{{ site.phone }}</a></div></div>
        <form class="request-form" @submit.prevent="submitForm">
          <label>Как вас зовут?<input v-model.trim="form.name" required minlength="2" placeholder="Ваше имя"></label>
          <label>Телефон<input v-model.trim="form.phone" required pattern="[+0-9 ()-]{7,}" placeholder="+7 999 000-00-00"></label>
          <label>E-mail<input v-model.trim="form.email" required type="email" placeholder="name@example.ru"></label>
          <label>Какой маршрут интересен?<select v-model="form.route"><option v-for="route in routes" :key="route.title">{{ route.title }}</option></select></label>
          <div v-if="form.departure_label" class="selected-departure"><span>Выбранный заезд</span><strong>{{ form.departure_label }}</strong><button type="button" @click="form.departure_id = ''; form.departure_label = ''">Изменить</button></div>
          <button class="submit" :disabled="sending">{{ sending ? 'Отправляем…' : 'Отправить заявку' }} <span>↗</span></button>
          <button type="button" class="payment-button" :disabled="paymentLoading" @click="startPayment">
            <span>{{ paymentLoading ? 'Создаём платёж…' : `Оплатить предоплату — ${Number(site.booking_deposit || 5000).toLocaleString('ru-RU')} ₽` }}</span>
            <b>ЮKassa</b>
          </button>
          <p class="payment-note">Вы перейдёте на защищённую тестовую страницу ЮKassa. Банковские данные сайт не хранит.</p>
          <p class="privacy">Нажимая кнопку, вы соглашаетесь с политикой конфиденциальности.</p>
          <p v-if="status" class="form-status" role="status">{{ status }}</p>
          <p v-if="paymentStatus" :class="['form-status', { paid: paymentStatus.includes('успешно') }]" role="status">{{ paymentStatus }}</p>
        </form>
      </section>
    </main>

    <div v-if="accountOpen" class="account-overlay" role="presentation" @click.self="closeAccount">
      <section class="account-modal" role="dialog" aria-modal="true" aria-labelledby="account-title">
        <button class="account-close" type="button" aria-label="Закрыть личный кабинет" @click="closeAccount">×</button>
        <template v-if="!account.authenticated">
          <div class="account-brand"><span>⌁</span><div><small>ВОЛЬНЫЙ АМУР</small><h2 id="account-title">{{ accountMode === 'login' ? 'Вход в кабинет' : 'Регистрация' }}</h2></div></div>
          <div class="account-tabs">
            <button :class="{ active: accountMode === 'login' }" @click="accountMode = 'login'; accountError = ''">Вход</button>
            <button :class="{ active: accountMode === 'register' }" @click="accountMode = 'register'; accountError = ''">Регистрация</button>
          </div>
          <form v-if="accountMode === 'login'" class="account-form" @submit.prevent="submitLogin">
            <label>E-mail<input v-model.trim="loginForm.email" type="email" autocomplete="email" required placeholder="name@example.ru"></label>
            <label>Пароль<input v-model="loginForm.password" type="password" autocomplete="current-password" required placeholder="Ваш пароль"></label>
            <button :disabled="accountLoading">{{ accountLoading ? 'Входим…' : 'Войти' }} <span>↗</span></button>
          </form>
          <form v-else class="account-form" @submit.prevent="submitRegistration">
            <label>Имя<input v-model.trim="registerForm.name" autocomplete="name" required minlength="2" placeholder="Как к вам обращаться"></label>
            <label>E-mail<input v-model.trim="registerForm.email" type="email" autocomplete="email" required placeholder="name@example.ru"></label>
            <label>Телефон<input v-model.trim="registerForm.phone" autocomplete="tel" pattern="[+0-9 ()-]{7,}" placeholder="+7 999 000-00-00"></label>
            <label>Пароль<input v-model="registerForm.password" type="password" autocomplete="new-password" minlength="8" required placeholder="Не менее 8 символов"></label>
            <button :disabled="accountLoading">{{ accountLoading ? 'Создаём кабинет…' : 'Зарегистрироваться' }} <span>↗</span></button>
          </form>
          <p v-if="accountError" class="account-error">{{ accountError }}</p>
          <p class="account-help">В кабинете сохраняются ваши заявки, даты заездов и платежи.</p>
        </template>
        <template v-else>
          <div class="account-profile-head">
            <div class="account-avatar">{{ account.user.name.slice(0, 1).toUpperCase() }}</div>
            <div><small>ЛИЧНЫЙ КАБИНЕТ</small><h2 id="account-title">{{ account.user.name }}</h2><p>{{ account.user.email }}<br>{{ account.user.phone }}</p></div>
            <button type="button" @click="logoutAccount">Выйти</button>
          </div>
          <div class="account-summary"><div><strong>{{ account.leads.length }}</strong><span>заявок</span></div><div><strong>{{ account.payments.length }}</strong><span>платежей</span></div></div>
          <div class="account-history">
            <section><h3>Мои заявки</h3><div v-if="account.leads.length" class="account-items"><article v-for="lead in account.leads" :key="lead.id"><div><strong>{{ lead.route }}</strong><span>{{ lead.departure }}</span></div><b>{{ lead.status }}</b><time>{{ lead.created_at }}</time></article></div><p v-else>Вы ещё не оставляли заявок.</p></section>
            <section><h3>Мои платежи</h3><div v-if="account.payments.length" class="account-items"><article v-for="payment in account.payments" :key="payment.id"><div><strong>{{ payment.route }}</strong><span>{{ Number(payment.amount).toLocaleString('ru-RU') }} ₽</span></div><b :class="{ paid: payment.paid }">{{ payment.status }}</b><time>{{ payment.created_at }}</time></article></div><p v-else>Платежей пока нет.</p></section>
          </div>
          <button class="account-main-action" type="button" @click="closeAccount(); scrollTo('calendar')">Выбрать новый заезд <span>↗</span></button>
          <p v-if="accountError" class="account-error">{{ accountError }}</p>
        </template>
      </section>
    </div>

    <button class="floating-contact" aria-label="Оставить заявку" @click="scrollTo('request')">
      <span>Обсудить маршрут</span><i>↗</i>
    </button>

    <footer><a class="logo inverted" href="#top"><span class="logo-mark">⌁</span><span>ВОЛЬНЫЙ<br><b>АМУР</b></span></a><p>Путешествия по Хабаровскому краю<br>с 2014 года</p><div><a href="#routes">Маршруты</a><a href="#guides">Наши специалисты</a><a href="#reviews">Отзывы</a><a href="#advantages">О нас</a></div><small>© 2026 Вольный Амур</small></footer>
  </div>
</template>
