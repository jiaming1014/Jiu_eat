const API_BASE = "http://127.0.0.1:8000";
const state = { activities: [], visible: 8, currentActivity: null };
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const memberId = () => Number(sessionStorage.getItem("memberId")) || null;

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) throw new Error(data?.detail || "操作失敗");
  return data;
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.remove("hidden");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.add("hidden"), 2800);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("zh-TW", { month: "numeric", day: "numeric", weekday: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function categoryIcon(category) {
  return ({ "美食饗宴": "🍱", "桌遊派對": "🎲", "歡唱 KTV": "🎤", "戶外運動": "⛰️", "咖啡閒聊": "☕" })[category] || "✨";
}

function cardHtml(item) {
  const remaining = Math.max(item.max_participants - item.approved_count, 0);
  const image = item.image_url || `https://picsum.photos/seed/jiueat${item.id}/600/400`;
  return `<button class="event-card" data-activity-id="${item.id}"><div class="card-img" style="background-image:url('${escapeHtml(image)}')"><span class="card-tag">${categoryIcon(item.category)} ${escapeHtml(item.category)}</span></div><div class="card-content"><div class="event-title">${escapeHtml(item.title)}</div><div class="event-info"><span>📍 ${escapeHtml(item.city)}・${escapeHtml(item.location_name)}</span><span>🗓 ${formatDate(item.activity_date)}</span></div><div class="card-footer"><span>發起人 ${escapeHtml(item.organizer_name)}</span><span class="status-badge">${remaining ? `還有 ${remaining} 個名額` : "已額滿"}</span></div></div></button>`;
}

function renderCards(container, items) {
  $(container).innerHTML = items.map(cardHtml).join("");
}

async function loadHome() {
  try {
    const activities = await api("/api/activities?limit=8");
    renderCards("#popular-grid", activities.slice(0, 4));
    $("#home-empty").classList.toggle("hidden", activities.length > 0);
    if (memberId()) {
      const recommendations = await api(`/api/recommendations/${memberId()}`);
      renderCards("#recommendation-grid", recommendations.slice(0, 4));
      $("#recommendation-note").textContent = recommendations.length ? "依你的興趣與常用地區排序。" : "目前沒有新的推薦活動。";
    } else {
      renderCards("#recommendation-grid", activities.slice(4, 8));
    }
  } catch (error) {
    $("#home-empty").classList.remove("hidden");
    $("#home-empty").textContent = "無法連接後端，請確認 FastAPI 已在 8000 埠啟動。";
  }
}

async function loadActivities() {
  const params = new URLSearchParams();
  const keyword = $("#filter-keyword").value.trim();
  const category = $("#filter-category").value;
  const city = $("#filter-city").value.trim();
  if (keyword) params.set("keyword", keyword);
  if (category) params.set("category", category);
  if (city) params.set("city", city);
  state.activities = await api(`/api/activities?${params}`);
  state.visible = 8;
  renderActivityList();
}

function renderActivityList() {
  renderCards("#activities-grid", state.activities.slice(0, state.visible));
  $("#activities-empty").classList.toggle("hidden", state.activities.length > 0);
  $("#load-more-button").classList.toggle("hidden", state.visible >= state.activities.length);
}

function requireLogin() {
  if (memberId()) return true;
  openAuth();
  showToast("請先登入會員");
  return false;
}

async function openDetail(id) {
  try {
    const item = await api(`/api/activities/${id}`);
    state.currentActivity = item;
    const mine = memberId() === item.organizer_id;
    const remaining = Math.max(item.max_participants - item.approved_count, 0);
    $("#activity-detail").innerHTML = `<div class="detail-image" style="background-image:url('${escapeHtml(item.image_url || `https://picsum.photos/seed/jiueat${item.id}/900/500`)}')"></div><div class="detail-body"><span class="section-kicker">${categoryIcon(item.category)} ${escapeHtml(item.category)}</span><h1>${escapeHtml(item.title)}</h1><div class="detail-meta"><span>📍 ${escapeHtml(item.city)}・${escapeHtml(item.location_name)}</span><span>🗓 ${formatDate(item.activity_date)}</span><span>⏳ 報名至 ${formatDate(item.deadline)}</span><span>👥 ${item.approved_count} / ${item.max_participants} 人</span></div><p class="detail-description">${escapeHtml(item.description || "發起人尚未填寫詳細說明。")}</p><p>發起人：<strong>${escapeHtml(item.organizer_name)}</strong></p><div class="detail-actions">${mine ? `<button class="button button-primary" data-edit-activity>編輯活動</button><button class="button button-outline" data-review-applicants>查看申請</button><button class="button button-outline" data-delete-activity>刪除活動</button>` : `<button class="button button-primary" data-apply-activity ${remaining === 0 ? "disabled" : ""}>${remaining ? "申請參加" : "活動已額滿"}</button>`}</div><div id="applicant-list" class="member-list"></div></div>`;
    location.hash = `#activity/${id}`;
  } catch (error) { showToast(error.message); }
}

function showPage(name) {
  $$(".page").forEach((page) => page.classList.remove("active"));
  $(`#${name}-page`)?.classList.add("active");
  $("#main-nav").classList.remove("open");
  window.scrollTo(0, 0);
}

async function route() {
  const hash = location.hash || "#home";
  if (hash.startsWith("#activity/")) return openDetail(Number(hash.split("/")[1]));
  if (hash === "#activities") { showPage("activities"); try { await loadActivities(); } catch (e) { showToast(e.message); } return; }
  if (hash === "#member") { if (!requireLogin()) return; showPage("member"); await loadMember(); return; }
  if (hash === "#create") { if (!requireLogin()) return; prepareActivityForm(); showPage("activity-form"); return; }
  showPage("home"); loadHome();
}

function openAuth(tab = "login-form") {
  $("#auth-modal").classList.remove("hidden");
  switchAuthTab(tab);
}
function closeAuth() { $("#auth-modal").classList.add("hidden"); }
function switchAuthTab(id) {
  $$(".auth-form").forEach((form) => form.classList.toggle("active", form.id === id));
  $$(".auth-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.authTab === id));
}
function updateAuthUi() {
  const loggedIn = Boolean(memberId());
  $$(".member-only").forEach((item) => item.classList.toggle("hidden", !loggedIn));
  $("#auth-button").textContent = loggedIn ? `登出 ${sessionStorage.getItem("displayName") || ""}` : "登入／註冊";
}

async function loadMember() {
  try {
    const [member, data] = await Promise.all([api(`/api/members/${memberId()}`), api(`/api/members/${memberId()}/activities`)]);
    $("#member-welcome").textContent = `${member.display_name}，在這裡管理你的資料與聚會。`;
    const form = $("#profile-form");
    ["email", "display_name", "city", "interests", "bio"].forEach((key) => form.elements[key].value = member[key] || "");
    $("#created-list").innerHTML = data.created.length ? data.created.map((item) => `<div class="member-item"><div><h3>${escapeHtml(item.title)}</h3><p>${formatDate(item.activity_date)}・${escapeHtml(item.city)}</p></div><div class="member-actions"><button class="button button-outline small" data-activity-id="${item.id}">查看</button><button class="button button-primary small" data-edit-id="${item.id}">編輯</button></div></div>`).join("") : `<p class="empty-state">你還沒有建立活動。</p>`;
    $("#applied-list").innerHTML = data.applications.length ? data.applications.map((item) => `<div class="member-item"><div><h3>${escapeHtml(item.activity_title)}</h3><p>申請時間 ${formatDate(item.created_at)}</p></div><div class="member-actions"><span class="status ${item.status}">${({pending:"待審核",approved:"已核准",rejected:"已拒絕",cancelled:"已取消"})[item.status]}</span>${item.status === "pending" ? `<button class="button button-outline small" data-cancel-id="${item.id}">取消申請</button>` : ""}</div></div>`).join("") : `<p class="empty-state">你目前沒有活動申請。</p>`;
  } catch (error) { showToast(error.message); }
}

function prepareActivityForm(item = null) {
  const form = $("#activity-form"); form.reset(); $("#activity-id").value = item?.id || "";
  $("#activity-form-title").textContent = item ? "編輯聚會" : "發起聚會";
  if (!item) return;
  ["title","description","category","city","location_name","max_participants","image_url"].forEach((key) => form.elements[key].value = item[key] || "");
  form.elements.activity_date.value = item.activity_date.slice(0,16); form.elements.deadline.value = item.deadline.slice(0,16);
}

async function reviewApplicants() {
  try {
    const items = await api(`/api/activities/${state.currentActivity.id}/applications?member_id=${memberId()}`);
    $("#applicant-list").innerHTML = items.length ? items.map((item) => `<div class="member-item"><div><h3>${escapeHtml(item.member_name)}</h3><p>${escapeHtml(item.message || "沒有留言")}</p></div><div class="member-actions"><span class="status ${item.status}">${item.status}</span>${item.status === "pending" ? `<button class="button button-primary small" data-approve-id="${item.id}">核准</button><button class="button button-outline small" data-reject-id="${item.id}">拒絕</button>` : ""}</div></div>`).join("") : `<p class="empty-state">目前還沒有申請人。</p>`;
  } catch (error) { showToast(error.message); }
}

document.addEventListener("click", async (event) => {
  const activityButton = event.target.closest("[data-activity-id]"); if (activityButton) return openDetail(Number(activityButton.dataset.activityId));
  if (event.target.closest("[data-back]")) { history.length > 1 ? history.back() : location.hash = "#activities"; return; }
  if (event.target.matches("[data-edit-activity]")) { prepareActivityForm(state.currentActivity); showPage("activity-form"); return; }
  if (event.target.matches("[data-review-applicants]")) return reviewApplicants();
  if (event.target.matches("[data-apply-activity]")) { if (!requireLogin()) return; const message = prompt("想對發起人說什麼？（可留空）") ?? ""; try { await api(`/api/activities/${state.currentActivity.id}/applications`, { method:"POST", body:JSON.stringify({member_id:memberId(), message}) }); showToast("申請已送出"); } catch(e){ showToast(e.message); } return; }
  if (event.target.matches("[data-delete-activity]")) { if (!confirm("確定刪除這場活動嗎？")) return; try { await api(`/api/activities/${state.currentActivity.id}?member_id=${memberId()}`, {method:"DELETE"}); showToast("活動已刪除"); location.hash="#member"; } catch(e){ showToast(e.message); } return; }
  const edit = event.target.closest("[data-edit-id]"); if (edit) { const item = await api(`/api/activities/${edit.dataset.editId}`); prepareActivityForm(item); showPage("activity-form"); return; }
  for (const action of ["approve","reject"]) { const btn=event.target.closest(`[data-${action}-id]`); if(btn){ try{ await api(`/api/applications/${btn.dataset[`${action}Id`]}/${action}?member_id=${memberId()}`,{method:"PUT"}); await reviewApplicants(); showToast("申請狀態已更新"); }catch(e){showToast(e.message)} return; }}
  const cancel=event.target.closest("[data-cancel-id]"); if(cancel){ try{ await api(`/api/applications/${cancel.dataset.cancelId}/cancel?member_id=${memberId()}`,{method:"PUT"}); await loadMember(); showToast("已取消申請"); }catch(e){showToast(e.message)} }
});

$("#auth-button").addEventListener("click", () => { if(memberId()){sessionStorage.clear(); updateAuthUi(); loadHome(); showToast("已登出");} else openAuth(); });
$("#create-button").addEventListener("click", () => { if(requireLogin()) location.hash="#create"; });
$("#menu-button").addEventListener("click", () => $("#main-nav").classList.toggle("open"));
$("#close-auth").addEventListener("click", closeAuth);
$("#auth-modal").addEventListener("click", (e) => { if(e.target.id === "auth-modal") closeAuth(); });
$$(".auth-tab").forEach((tab) => tab.addEventListener("click", () => switchAuthTab(tab.dataset.authTab)));
$("#login-form").addEventListener("submit", async (e) => { e.preventDefault(); const form=new FormData(e.target); try{const data=await api("/api/login",{method:"POST",body:JSON.stringify(Object.fromEntries(form))}); sessionStorage.setItem("memberId",data.member_id);sessionStorage.setItem("displayName",data.display_name);updateAuthUi();closeAuth();loadHome();showToast("登入成功");}catch(error){showToast(error.message)} });
$("#register-form").addEventListener("submit", async (e) => { e.preventDefault(); const payload=Object.fromEntries(new FormData(e.target)); try{await api("/api/register",{method:"POST",body:JSON.stringify(payload)});showToast("註冊成功，請登入");switchAuthTab("login-form");$("#login-form").elements.email.value=payload.email;}catch(error){showToast(error.message)} });
$("#home-search-form").addEventListener("submit", (e) => { e.preventDefault(); $("#filter-keyword").value=$("#home-keyword").value; location.hash="#activities"; });
$$("#home-categories .category-chip").forEach((chip) => chip.addEventListener("click", () => { $("#filter-category").value=chip.dataset.category; location.hash="#activities"; }));
$("#filter-form").addEventListener("submit", (e) => { e.preventDefault(); loadActivities().catch(error=>showToast(error.message)); });
$("#load-more-button").addEventListener("click", () => { state.visible+=8; renderActivityList(); });
$$(".tab").forEach((tab) => tab.addEventListener("click", () => { $$(".tab").forEach(t=>t.classList.remove("active")); $$(".tab-panel").forEach(p=>p.classList.remove("active")); tab.classList.add("active"); $(`#${tab.dataset.tab}`).classList.add("active"); }));
$("#profile-form").addEventListener("submit", async(e)=>{e.preventDefault();const payload=Object.fromEntries(new FormData(e.target));delete payload.email;try{const data=await api(`/api/members/${memberId()}`,{method:"PUT",body:JSON.stringify(payload)});sessionStorage.setItem("displayName",data.display_name);updateAuthUi();showToast("個人資料已更新");}catch(error){showToast(error.message)}});
$("#activity-form").addEventListener("submit", async(e)=>{e.preventDefault();const payload=Object.fromEntries(new FormData(e.target));payload.organizer_id=memberId();payload.max_participants=Number(payload.max_participants);payload.activity_date=new Date(payload.activity_date).toISOString();payload.deadline=new Date(payload.deadline).toISOString();const id=$("#activity-id").value;try{const data=await api(id?`/api/activities/${id}`:"/api/activities",{method:id?"PUT":"POST",body:JSON.stringify(payload)});showToast(id?"活動已更新":"活動已建立");openDetail(data.id);}catch(error){showToast(error.message)}});
window.addEventListener("hashchange", route);
updateAuthUi(); route();
