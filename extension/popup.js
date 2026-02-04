const PYTHON_BACKEND = "http://localhost:5000";

const views = {
    me: document.getElementById('view-me'),
    friends: document.getElementById('view-friends')
};
const tabs = {
    me: document.getElementById('tab-me'),
    friends: document.getElementById('tab-friends')
};

const usernameInput = document.getElementById('username-input');
const friendInput = document.getElementById('friend-input');

const setupSection = document.getElementById('setup-section');
const statsSection = document.getElementById('stats-section');
const recommendationsList = document.getElementById('recommendations-list');
const friendResult = document.getElementById('friend-result');

let currentUser = null;

document.addEventListener('DOMContentLoaded', async () => {
    loadTabs();
    const stored = await chrome.storage.local.get(['leetcode_username']);
    if (stored.leetcode_username) {
        currentUser = stored.leetcode_username;
        showStats();
    } else {
        showSetup();
    }
});

function loadTabs() {
    tabs.me.addEventListener('click', () => switchTab('me'));
    tabs.friends.addEventListener('click', () => switchTab('friends'));
}

function switchTab(tabName) {
    Object.values(views).forEach(el => el.classList.remove('active', 'hidden'));
    Object.values(tabs).forEach(el => el.classList.remove('active'));
    views[tabName].classList.add('active');
    tabs[tabName].classList.add('active');
}


document.getElementById('save-user-btn').addEventListener('click', async () => {
    const user = usernameInput.value.trim();
    if (!user) return;
    await chrome.storage.local.set({ leetcode_username: user });
    currentUser = user;
    showStats();
});

document.getElementById('change-user-btn').addEventListener('click', async () => {
    await chrome.storage.local.remove(['leetcode_username']);
    currentUser = null;
    showSetup();
});

document.getElementById('refresh-btn').addEventListener('click', () => {
    fetchUserData(currentUser);
});

function showSetup() {
    setupSection.classList.remove('hidden');
    statsSection.classList.add('hidden');
}

function showStats() {
    setupSection.classList.add('hidden');
    statsSection.classList.remove('hidden');
    document.getElementById('display-username').textContent = currentUser;
    fetchUserData(currentUser);
}


async function fetchUserData(username) {
    document.getElementById('easy-count').textContent = '-';
    document.getElementById('medium-count').textContent = '-';
    document.getElementById('hard-count').textContent = '-';

    try {
        const resp = await fetch(`${PYTHON_BACKEND}/profile`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username })
        });

        if (!resp.ok) throw new Error("Backend Error");
        const stats = await resp.json();

        const getCount = (diff) => (stats.find(s => s.difficulty === diff) || {}).count || 0;

        document.getElementById('easy-count').textContent = getCount("Easy");
        document.getElementById('medium-count').textContent = getCount("Medium");
        document.getElementById('hard-count').textContent = getCount("Hard");

        fetchRecommendations();

    } catch (e) {
        document.getElementById('display-username').textContent = `${username} (Error/Offline)`;
    }
}

async function fetchRecommendations() {
    recommendationsList.innerHTML = '<div class="loading">Consulting Python Logic...</div>';



    try {
        const resp = await fetch(`${PYTHON_BACKEND}/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tags: [], recent: [] })
        });

        if (!resp.ok) throw new Error("Python server offline");
        const mlData = await resp.json();

        const recs = (mlData.recommendations || []).slice(0, 5).map(r => ({
            title: r.title,
            titleSlug: r.titleSlug,
            difficulty: r.difficulty,
            topicTags: (r.topics || []).map(t => ({ name: t }))
        }));

        if (recs.length === 0) throw new Error("No recs returned");
        renderRecommendations(recs);

    } catch (e) {
        recommendationsList.innerHTML = '<div class="faded">Python backend offline.</div>';
    }
}

function renderRecommendations(recs) {
    recommendationsList.innerHTML = '';
    recs.forEach(p => {
        const el = document.createElement('a');
        el.className = `rec-item ${p.difficulty}`;
        el.href = `https://leetcode.com/problems/${p.titleSlug}/`;
        el.target = "_blank";
        el.innerHTML = `
      <span class="title">${p.title}</span>
      <span class="meta">${p.difficulty} • ${(p.topicTags || []).map(t => t.name).join(', ')}</span>
    `;
        recommendationsList.appendChild(el);
    });
}

document.getElementById('search-friend-btn').addEventListener('click', async () => {
    const friendName = friendInput.value.trim();
    if (!friendName) return;

    friendResult.classList.remove('hidden');
    document.getElementById('friend-username').textContent = "Loading...";
    document.getElementById('friend-solved-list').innerHTML = '';

    try {
        const resp = await fetch(`${PYTHON_BACKEND}/friend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: friendName })
        });

        const data = await resp.json();

        if (data && data.data && data.data.matchedUser) {
            document.getElementById('friend-username').textContent = friendName;
            const total = data.data.matchedUser.submitStats.acSubmissionNum.find(s => s.difficulty === "All").count;
            document.getElementById('friend-total').textContent = total;

            const list = document.getElementById('friend-solved-list');
            list.innerHTML = '';

            const recent = data.data.recentSubmissionList || [];
            if (recent.length === 0) {
                list.innerHTML = '<li><span style="color:#666">No recent public activity</span></li>';
            }

            recent.forEach(sub => {
                const li = document.createElement('li');
                const date = new Date(sub.timestamp * 1000);
                li.innerHTML = `
                    <span>${sub.title}</span>
                    <span class="timestamp">${date.toLocaleDateString()}</span> 
                `;
                list.appendChild(li);
            });

        } else {
            throw new Error("User not found");
        }

    } catch (e) {
        document.getElementById('friend-username').textContent = "User not found";
        document.getElementById('friend-total').textContent = "-";
    }
});
