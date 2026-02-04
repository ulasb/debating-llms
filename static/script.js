let eventSource = null;
let currentTranscriptLength = 0;

// On load, fetch models
window.addEventListener('DOMContentLoaded', async () => {
    await populateModels();
});

async function populateModels() {
    try {
        const res = await fetch('/models');
        const data = await res.json();
        const models = data.models || ["gemma3:1b"];

        const selects = document.getElementsByClassName('model-select');
        for (let select of selects) {
            select.innerHTML = ''; // Clear loading
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                select.appendChild(opt);
            });
            // Try to set default to gemma3:1b if available, else first
            if (models.includes("gemma3:1b")) {
                select.value = "gemma3:1b";
            }
        }
    } catch (e) {
        console.error("Failed to load models", e);
    }
}

function showError(msg) {
    const el = document.getElementById('error-banner');
    el.textContent = msg;
    el.classList.remove('hidden');
    setTimeout(() => {
        el.classList.add('hidden');
    }, 5000);
}

async function startDebate() {
    const topic = document.getElementById('topic').value;
    const rounds = parseInt(document.getElementById('rounds').value);

    // Collect models for each role
    const model_mod = document.getElementById('model-mod').value;
    const model_prop = document.getElementById('model-prop').value;
    const model_opp = document.getElementById('model-opp').value;

    const btn = document.getElementById('startBtn');
    btn.disabled = true;

    try {
        const response = await fetch('/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic,
                rounds,
                model_mod,
                model_prop,
                model_opp
            })
        });
        const result = await response.json();

        if (result.success) {
            connectStream();
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
        } else {
            showError('Failed to start: ' + result.message);
            btn.disabled = false;
        }
    } catch (e) {
        console.error(e);
        showError('Network error or server unavailable');
        btn.disabled = false;
    }
}

async function stopDebate() {
    await fetch('/stop', { method: 'POST' });
}

function connectStream() {
    if (eventSource) eventSource.close();

    eventSource = new EventSource('/stream');

    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        render(data);


        if (data.status === 'completed' || data.status === 'error') {
            eventSource.close();
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status-text').textContent = data.status === 'completed' ? 'Finished' : 'Error';

            if (data.status === 'error' && data.error) {
                showError(data.error);
            }

            document.getElementById('typing-indicator').classList.add('hidden');
        }
    };

    eventSource.onerror = function () {
        // console.log("Stream connection lost/closed.");
        // eventSource.close();
    };
}

function render(data) {
    const messagesDiv = document.getElementById('messages');
    const statusText = document.getElementById('status-text');
    const roundIndicator = document.getElementById('round-indicator');
    const typingIndicator = document.getElementById('typing-indicator');
    const typerName = document.getElementById('typer-name');

    // Status
    statusText.textContent = data.status.toUpperCase();
    if (data.status === 'running') {
        roundIndicator.textContent = `Round ${data.rounds_current} / ${data.rounds_total}`;
    }

    // Append finalized messages
    if (data.transcript.length > currentTranscriptLength) {
        // Add new messages
        for (let i = currentTranscriptLength; i < data.transcript.length; i++) {
            const turn = data.transcript[i];
            const div = createMessageDiv(turn.speaker, turn.content);
            messagesDiv.appendChild(div);
        }
        currentTranscriptLength = data.transcript.length;
        scrollToBottom();
    }

    // Handle Streaming (ghost message)
    let streamDiv = document.getElementById('streaming-msg');

    if (data.current_stream) {
        typingIndicator.classList.add('hidden');

        if (!streamDiv) {
            streamDiv = createMessageDiv(data.current_speaker, '', true);
            streamDiv.id = 'streaming-msg';
            messagesDiv.appendChild(streamDiv);
        } else {
            // Update speaker if changed (rare but possible in transitions)
            // But mainly update content
            const contentSpan = streamDiv.querySelector('.content');
            contentSpan.innerText = data.current_stream;

            // Ensure class is correct
            streamDiv.className = `message ${data.current_speaker.toLowerCase()} streaming`;
        }
        scrollToBottom();
    } else {
        // No active stream
        if (streamDiv) {
            streamDiv.remove();
        }

        // Show typing if running and no stream
        if (data.status === 'running') {
            typingIndicator.classList.remove('hidden');
            typerName.textContent = data.current_speaker || "Agent";
        } else {
            typingIndicator.classList.add('hidden');
        }
    }
}

function createMessageDiv(speaker, content, isStreaming = false) {
    const div = document.createElement('div');
    div.className = `message ${speaker.toLowerCase()} ${isStreaming ? 'streaming' : ''}`;

    const label = document.createElement('span');
    label.className = 'role-label';
    label.textContent = speaker;

    const text = document.createElement('div');
    text.className = 'content';
    // Use marked and DOMPurify for safe markdown rendering
    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
        text.innerHTML = DOMPurify.sanitize(marked.parse(content));
    } else {
        text.innerText = content;
    }

    div.appendChild(label);
    div.appendChild(text);
    return div;
}

function scrollToBottom() {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
