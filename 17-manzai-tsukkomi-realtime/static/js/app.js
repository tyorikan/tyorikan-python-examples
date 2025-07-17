/**
 * 漫才ツッコミ Web アプリ - フロントエンド JavaScript
 */

class TsukkomiApp {
    constructor() {
        this.ws = null;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.connectionId = null;
        
        // DOM要素
        this.elements = {
            recordButton: document.getElementById('recordButton'),
            textInput: document.getElementById('textInput'),
            sendTextButton: document.getElementById('sendTextButton'),
            conversationContainer: document.getElementById('conversationContainer'),
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.getElementById('statusText'),
            connectionCount: document.getElementById('connectionCount'),
            requestCount: document.getElementById('requestCount'),
            audioVisualizer: document.getElementById('audioVisualizer'),
            audioPlayer: document.getElementById('audioPlayer')
        };
        
        this.init();
    }
    
    async init() {
        console.log('🎭 漫才ツッコミアプリを初期化中...');
        
        // WebSocket接続
        await this.connectWebSocket();
        
        // イベントリスナーの設定
        this.setupEventListeners();
        
        // 音声権限の確認
        await this.checkAudioPermissions();
        
        // 統計情報の定期更新
        // this.startStatsUpdate();
        
        console.log('✅ アプリの初期化が完了しました');
    }
    
    async connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.updateConnectionStatus('connecting', '接続中...');
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = (event) => {
                console.log('🔌 WebSocket接続が確立されました');
                this.updateConnectionStatus('connected', '接続済み');
            };
            
            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(JSON.parse(event.data));
            };
            
            this.ws.onclose = (event) => {
                console.log('🔌 WebSocket接続が切断されました');
                this.updateConnectionStatus('disconnected', '切断');
                
                // 自動再接続
                setTimeout(() => {
                    this.connectWebSocket();
                }, 3000);
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocketエラー:', error);
                this.updateConnectionStatus('disconnected', 'エラー');
            };
            
        } catch (error) {
            console.error('❌ WebSocket接続エラー:', error);
            this.updateConnectionStatus('disconnected', '接続失敗');
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('📨 WebSocketメッセージ受信:', data);
        
        switch (data.type) {
            case 'connection_established':
                this.connectionId = data.connection_id;
                this.addMessage('system', data.message);
                break;
                
            case 'tsukkomi_response':
                this.handleTsukkomiResponse(data);
                break;
                
            case 'error':
                this.addMessage('error', `エラー: ${data.message}`);
                break;
                
            case 'pong':
                // 接続確認レスポンス
                break;
                
            default:
                console.log('未知のメッセージタイプ:', data.type);
        }
    }
    
    handleTsukkomiResponse(data) {
        // ツッコミテキストを表示
        this.addMessage('ai', data.text, data.timestamp);
        
        // 音声データがある場合は再生
        if (data.audio_data) {
            this.playAudio(data.audio_data);
        }
        
        // 元のテキストがある場合はユーザーメッセージとして表示
        if (data.original_text) {
            this.addMessage('user', data.original_text, data.timestamp);
        }
    }
    
    async playAudio(audioDataBase64) {
        try {
            // Base64データをBlobに変換
            const audioData = atob(audioDataBase64);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const uint8Array = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                uint8Array[i] = audioData.charCodeAt(i);
            }
            
            const blob = new Blob([arrayBuffer], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(blob);
            
            this.elements.audioPlayer.src = audioUrl;
            await this.elements.audioPlayer.play();
            
            // メモリリークを防ぐためURLを解放
            this.elements.audioPlayer.onended = () => {
                URL.revokeObjectURL(audioUrl);
            };
            
        } catch (error) {
            console.error('❌ 音声再生エラー:', error);
        }
    }
    
    setupEventListeners() {
        // 録音ボタン
        this.elements.recordButton.addEventListener('mousedown', () => {
            this.startRecording();
        });
        
        this.elements.recordButton.addEventListener('mouseup', () => {
            this.stopRecording();
        });
        
        this.elements.recordButton.addEventListener('mouseleave', () => {
            if (this.isRecording) {
                this.stopRecording();
            }
        });
        
        // タッチデバイス対応
        this.elements.recordButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        
        this.elements.recordButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        
        // テキスト送信
        this.elements.sendTextButton.addEventListener('click', () => {
            this.sendTextMessage();
        });
        
        this.elements.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTextMessage();
            }
        });
        
        // ページ離脱時のクリーンアップ
        window.addEventListener('beforeunload', () => {
            if (this.ws) {
                this.ws.close();
            }
        });
    }
    
    async checkAudioPermissions() {
        try {
            // まずマイクが利用可能かチェック
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('このブラウザは音声録音をサポートしていません');
            }

            console.log('🎤 マイク権限を確認中...');
            
            // マイク権限をリクエスト
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // ストリームを即座に停止
            stream.getTracks().forEach(track => track.stop());
            
            // ボタンを有効化
            this.elements.recordButton.disabled = false;
            this.elements.recordButton.style.opacity = '1';
            this.elements.recordButton.style.cursor = 'pointer';
            
            // ボタンの表示を更新
            this.elements.recordButton.innerHTML = '<i class="fas fa-microphone"></i><span class="button-text">マイクをタップして話す</span>';
            
            // ヒントテキストを更新
            const hintText = document.getElementById('hintText');
            if (hintText) {
                hintText.textContent = 'マイクボタンを押して話しかけてください。AIが関西弁でツッコミを入れます！';
            }
            
            console.log('✅ 音声権限が許可されました');
            this.addMessage('system', '✅ マイクの使用が許可されました。ボタンを押して話しかけてください！');
            
        } catch (error) {
            console.error('❌ 音声権限エラー:', error);
            
            this.elements.recordButton.disabled = true;
            this.elements.recordButton.style.opacity = '0.5';
            this.elements.recordButton.style.cursor = 'not-allowed';
            
            let errorMessage = 'マイクへのアクセス権限が必要です。';
            
            if (error.name === 'NotAllowedError') {
                errorMessage += 'ブラウザでマイクの使用を許可してください。';
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'マイクが見つかりません。マイクが接続されているか確認してください。';
            } else if (error.name === 'NotSupportedError') {
                errorMessage += 'このブラウザは音声録音をサポートしていません。';
            } else {
                errorMessage += `エラー: ${error.message}`;
            }
            
            this.addMessage('error', errorMessage);
            
            // 権限取得のためのボタンを表示
            this.showPermissionButton();
        }
    }
    
    showPermissionButton() {
        // 既存の権限ボタンがあれば削除
        const existingButton = document.querySelector('.permission-button');
        if (existingButton) {
            existingButton.remove();
        }
        
        // 権限取得用のボタンを表示
        const permissionButton = document.createElement('button');
        permissionButton.className = 'permission-button';
        permissionButton.innerHTML = '<i class="fas fa-microphone-slash"></i> マイク権限を許可';
        permissionButton.onclick = () => {
            this.checkAudioPermissions();
            permissionButton.remove();
        };
        
        // ヒントテキストを更新
        const hintText = document.getElementById('hintText');
        if (hintText) {
            hintText.innerHTML = '<i class="fas fa-exclamation-triangle"></i> マイクの使用許可が必要です。下のボタンをクリックしてください。';
        }
        
        // ボタンをマイクボタンの下に追加
        this.elements.recordButton.parentNode.appendChild(permissionButton);
    }
    
    async startRecording() {
        if (this.isRecording || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            this.isRecording = true;
            
            // UI更新
            this.elements.recordButton.classList.add('recording');
            this.elements.recordButton.innerHTML = '<i class="fas fa-stop"></i><span class="button-text">録音中...</span>';
            this.elements.audioVisualizer.classList.add('active');
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecordedAudio();
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.start(100); // 100ms間隔でデータを収集
            
            console.log('🎤 録音を開始しました');
            
        } catch (error) {
            console.error('❌ 録音開始エラー:', error);
            this.addMessage('error', '録音の開始に失敗しました');
        }
    }
    
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            return;
        }
        
        this.isRecording = false;
        this.mediaRecorder.stop();
        
        // UI更新
        this.elements.recordButton.classList.remove('recording');
        this.elements.recordButton.innerHTML = '<i class="fas fa-microphone"></i><span class="button-text">マイクをタップして話す</span>';
        this.elements.audioVisualizer.classList.remove('active');
        
        console.log('🎤 録音を停止しました');
    }
    
    async processRecordedAudio() {
        if (this.audioChunks.length === 0) {
            return;
        }
        
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            const arrayBuffer = await audioBlob.arrayBuffer();
            const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
            
            // WebSocket経由で音声データを送信
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'audio_data',
                    audio_data: base64Audio,
                    timestamp: new Date().toISOString()
                }));
                
                console.log('📤 音声データを送信しました');
                this.addMessage('user', '🎤 音声メッセージ');
            }
            
        } catch (error) {
            console.error('❌ 音声処理エラー:', error);
            this.addMessage('error', '音声の処理に失敗しました');
        }
    }
    
    sendTextMessage() {
        const text = this.elements.textInput.value.trim();
        if (!text || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        // WebSocket経由でテキストを送信
        this.ws.send(JSON.stringify({
            type: 'text_message',
            text: text,
            timestamp: new Date().toISOString()
        }));
        
        this.elements.textInput.value = '';
        console.log('📤 テキストメッセージを送信しました:', text);
    }
    
    addMessage(type, content, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = timestamp ? 
            new Date(timestamp).toLocaleTimeString() : 
            new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampDiv);
        
        // ウェルカムメッセージを削除
        const welcomeMessage = this.elements.conversationContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        this.elements.conversationContainer.appendChild(messageDiv);
        this.elements.conversationContainer.scrollTop = this.elements.conversationContainer.scrollHeight;
    }
    
    updateConnectionStatus(status, text) {
        this.elements.statusIndicator.className = `fas fa-circle status-indicator ${status}`;
        this.elements.statusText.textContent = text;
    }
    
    async startStatsUpdate() {
        setInterval(async () => {
            try {
                const response = await fetch('/stats');
                const stats = await response.json();
                
                this.elements.connectionCount.textContent = stats.active_connections || '-';
                this.elements.requestCount.textContent = stats.processor_status?.request_count || '-';
                
            } catch (error) {
                console.error('統計情報の取得に失敗:', error);
            }
        }, 5000); // 5秒間隔で更新
    }
    
    // 接続確認のためのping送信
    startHeartbeat() {
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'ping',
                    timestamp: new Date().toISOString()
                }));
            }
        }, 30000); // 30秒間隔
    }
    
    // デバッグ情報の表示
    showDebugInfo() {
        const debugInfo = {
            'WebSocket状態': this.ws ? this.ws.readyState : 'なし',
            'マイク権限': this.elements.recordButton.disabled ? '未許可' : '許可済み',
            '録音状態': this.isRecording ? '録音中' : '停止中',
            'ブラウザ': navigator.userAgent,
            'HTTPS': window.location.protocol === 'https:' ? 'はい' : 'いいえ',
            'MediaDevices対応': navigator.mediaDevices ? 'はい' : 'いいえ'
        };
        
        console.log('🔍 デバッグ情報:', debugInfo);
        return debugInfo;
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.tsukkomiApp = new TsukkomiApp();
});