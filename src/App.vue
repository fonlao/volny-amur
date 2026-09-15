<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

const menuOpen = ref(false)
const activeRoute = ref(0)
const activeMapRoute = ref(0)
const activeFaq = ref(0)
const mapElement = ref(null)
const mapMessage = ref('')
const theme = ref('light')
const sending = ref(false)
const status = ref('')
const paymentLoading = ref(false)
const paymentStatus = ref('')
const form = ref({ name: '', phone: '', email: '', route: 'Шантарские острова' })
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

onMounted(async () => {
  try {
    const response = await fetch('/api/content')
    if (!response.ok) return
    const data = await response.json()
    site.value = data.site
    if (data.advantages?.length) advantages.value = data.advantages
    if (data.routes?.length) {
      routes.value = data.routes.map((item, index) => ({ ...item, number: String(index + 1).padStart(2, '0'), art: item.visual_style }))
      form.value.route = routes.value[0].title
    }
    if (data.guides?.length) guides.value = data.guides.map(item => ({ ...item, exp: item.experience }))
  } catch (_) {
    // Встроенное содержимое остаётся доступным, если API временно недоступен.
  } finally {
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
</script>

<template>
  <div class="site-shell">
    <header class="header">
      <a class="logo" href="#top" aria-label="Вольный Амур — главная"><span class="logo-mark">⌁</span><span>ВОЛЬНЫЙ<br><b>АМУР</b></span></a>
      <nav :class="['nav', { open: menuOpen }]">
        <button @click="scrollTo('advantages')">О нас</button><button @click="scrollTo('routes')">Маршруты</button><button @click="scrollTo('route-map')">Карта</button><button @click="scrollTo('guides')">Наши специалисты</button>
      </nav>
      <button class="header-cta" @click="scrollTo('request')">Подобрать маршрут <span>↗</span></button>
      <button class="theme-toggle" type="button" :aria-label="theme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему'" :title="theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'" @click="toggleTheme"><span>{{ theme === 'dark' ? '☀' : '☾' }}</span></button>
      <button class="menu" @click="menuOpen = !menuOpen" aria-label="Меню">{{ menuOpen ? '×' : '☰' }}</button>
    </header>

    <main>
      <section id="top" class="hero">
        <div class="hero-art" aria-hidden="true">
          <div class="sun"></div><div class="cloud c1"></div><div class="cloud c2"></div>
          <div class="mountain m-back"></div><div class="mountain m-mid"></div><div class="mountain m-front"></div>
          <div class="river"></div><div class="tree t1">▲</div><div class="tree t2">▲</div><div class="tree t3">▲</div><div class="tree t4">▲</div>
        </div>
        <div class="hero-grid">
          <div class="eyebrow"><span></span> {{ site.hero_eyebrow }}</div>
          <h1>{{ splitTitle(site.hero_title).lead }}<br><em>{{ splitTitle(site.hero_title).accent }}</em></h1>
          <p class="hero-copy">{{ site.hero_text }}</p>
          <button class="primary" @click="scrollTo('routes')">Исследовать маршруты <span>↓</span></button>
          <div class="hero-note"><b>49°</b><span>северной широты<br>территория свободы</span></div>
        </div>
        <div class="scroll-label">ЛИСТАЙТЕ, ЧТОБЫ УЗНАТЬ БОЛЬШЕ <i></i></div>
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

      <section id="guides" class="guides section-pad">
        <div class="section-kicker">05 / НАШИ СПЕЦИАЛИСТЫ</div>
        <div class="section-heading"><h2>{{ splitTitle(site.guides_title).lead }}<br><em>{{ splitTitle(site.guides_title).accent }}</em></h2><p>Наши гиды не просто показывают дорогу. Они помогают почувствовать место.</p></div>
        <div class="guide-grid">
          <article v-for="guide in guides" :key="guide.name">
            <div :class="['guide-photo', guide.color, { 'has-image': guide.image_url }]" :style="guide.image_url ? { backgroundImage: `url(${guide.image_url})` } : {}"><span>{{ guide.initials }}</span><div class="ridge"></div></div>
            <div class="guide-content"><small>{{ guide.role }}</small><h3>{{ guide.name }}</h3><p>«{{ guide.quote }}»</p><span class="experience">{{ guide.exp }}</span></div>
          </article>
        </div>
      </section>

      <section id="faq" class="faq section-pad">
        <div class="section-kicker">06 / ВАЖНО ЗНАТЬ</div>
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
        <div class="request-copy"><div class="section-kicker light">07 / НАЧНЁМ?</div><h2>{{ splitTitle(site.request_title).lead }}<br><em>{{ splitTitle(site.request_title).accent }}</em></h2><p>{{ site.request_text }}</p><div class="contact-line"><span>или напишите нам</span><a :href="`mailto:${site.email}`">{{ site.email }}</a><a :href="`tel:${site.phone.replace(/[^+\d]/g, '')}`">{{ site.phone }}</a></div></div>
        <form class="request-form" @submit.prevent="submitForm">
          <label>Как вас зовут?<input v-model.trim="form.name" required minlength="2" placeholder="Ваше имя"></label>
          <label>Телефон<input v-model.trim="form.phone" required pattern="[+0-9 ()-]{7,}" placeholder="+7 999 000-00-00"></label>
          <label>E-mail<input v-model.trim="form.email" required type="email" placeholder="name@example.ru"></label>
          <label>Какой маршрут интересен?<select v-model="form.route"><option v-for="route in routes" :key="route.title">{{ route.title }}</option></select></label>
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

    <button class="floating-contact" aria-label="Оставить заявку" @click="scrollTo('request')">
      <span>Обсудить маршрут</span><i>↗</i>
    </button>

    <footer><a class="logo inverted" href="#top"><span class="logo-mark">⌁</span><span>ВОЛЬНЫЙ<br><b>АМУР</b></span></a><p>Путешествия по Хабаровскому краю<br>с 2014 года</p><div><a href="#routes">Маршруты</a><a href="#guides">Наши специалисты</a><a href="#advantages">О нас</a></div><small>© 2026 Вольный Амур</small></footer>
  </div>
</template>
