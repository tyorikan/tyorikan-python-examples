const demoForm = document.getElementById('demo-form');

demoForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    // 画像ファイルを取得
    const imageFile = demoForm.querySelector('input[type="file"][name="image"]').files[0];

    // 画像ファイルのみを含む FormData を作成
    const imageFormData = new FormData();
    imageFormData.append("image", imageFile);

    // 画像ファイルをアップロード
    const uploadResponse = await fetch('/api/upload-image', {
        method: 'POST',
        body: imageFormData
    });

    if (!uploadResponse.ok) {
        alert("画像のアップロードに失敗しました。");
        return;
    }

    // アップロードされた画像の URL を取得 (API のレスポンス形式に合わせて調整)
    const uploadResult = await uploadResponse.json();
    const imagePath = uploadResult.object_path;

    // 元の FormData にダウンロード URL を追加
    // const originalFormData = new FormData(demoForm);
    // originalFormData.append("image_path", imagePath);

    // TODO: Dummy data
    const originalFormData = {
      "title": "東京本社火災",
      "submit_date": "2023-01-01",
      "location_id": 1,
      "department_id": 1,
      "type": "災害",
      "occurred_at": "2023-01-01 00:00:00",
      "occurred_place_id": 1,
      "occurred_place_detail": "本社ビル",
      "cause_id": 1,
      "witness_id": 1,
      "witness_manager_id": 2,
      "reporter_id": 1,
      "reporter_phone_number": "0123456789",
      "manager_id": 2,
      "worker_id": 1,
      "work_members": "佐藤 凛",
      "disaster_type_id": 1,
      "injury_classification_id": 1,
      "injured_part_id": 1,
      "injury_description": "軽度のやけど",
      "description": "出火場所は本社ビルの3階です。",
      "image_path": imagePath
    }

    // フォームデータを API に送信
    const response = await fetch("/api/incidents", {
        method: "POST",
        body: originalFormData,
    });

    // レスポンスを処理
    if (response.ok) {
        alert("第一報が送信されました。");
    } else {
        alert("第一報の送信に失敗しました。");
    }
});
