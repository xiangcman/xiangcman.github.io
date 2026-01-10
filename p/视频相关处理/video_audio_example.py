#!/usr/bin/env python3
"""
视频音频处理示例
展示如何使用 VideoAudioProcessor 的各种功能
"""

from video_audio_processor import VideoAudioProcessor


def example_1_extract_audio():
    """示例 1: 提取视频中的音频"""
    print("=" * 60)
    print("示例 1: 提取音频")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 提取为 MP3
    audio_file = processor.extract_audio(format="mp3", quality="192k")
    if audio_file:
        print(f"✅ 音频已提取: {audio_file}")

    # 提取为 WAV（无损）
    audio_file_wav = processor.extract_audio(format="wav")
    if audio_file_wav:
        print(f"✅ 音频已提取（WAV）: {audio_file_wav}")


def example_2_separate_vocals_bgm():
    """示例 2: 分离人声和 BGM（推荐使用 audio-separator）"""
    print("=" * 60)
    print("示例 2: 分离人声和 BGM")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 方法 1: 使用 audio-separator（推荐，不依赖旧版 numpy）
    print("\n尝试方法 1: audio-separator（推荐）")
    result = processor.extract_bgm_demucs_cli(model="htdemucs")
    
    if not result:
        # 方法 2: 使用 Spleeter（备选）
        print("\n尝试方法 2: Spleeter")
        result = processor.extract_bgm_spleeter()
    
    if not result:
        # 方法 3: 使用 FFmpeg 简单方法（效果一般，但无需额外依赖）
        print("\n尝试方法 3: FFmpeg 简单方法（效果有限）")
        result = processor.extract_bgm_ffmpeg_center()

    if result:
        vocals_file, bgm_file = result
        print(f"\n✅ 人声文件: {vocals_file}")
        print(f"✅ BGM 文件: {bgm_file}")
    else:
        print("\n❌ 所有方法都失败")
        print("   推荐安装: pip install audio-separator")
        print("   或安装: pip install spleeter")


def example_3_remove_vocals():
    """示例 3: 去除人声，保留 BGM"""
    print("=" * 60)
    print("示例 3: 去除人声，保留 BGM")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 1. 分离音频（使用 Demucs）
    result = processor.extract_bgm_demucs_cli(model="htdemucs")
    if not result:
        print("❌ 无法分离音频")
        print("   请确保已安装 Demucs: pip install demucs")
        return

    vocals_file, bgm_file = result

    # 2. 用 BGM 替换原视频的音频
    output_video = processor.replace_audio(bgm_file)
    if output_video:
        print(f"✅ 已去除人声: {output_video}")


def example_4_remove_bgm():
    """示例 4: 去除 BGM，保留人声"""
    print("=" * 60)
    print("示例 4: 去除 BGM，保留人声")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 1. 分离音频（使用 Demucs）
    result = processor.extract_bgm_demucs_cli(model="htdemucs")
    if not result:
        print("❌ 无法分离音频")
        print("   请确保已安装 Demucs: pip install demucs")
        return

    vocals_file, bgm_file = result

    # 2. 用人声替换原视频的音频
    output_video = processor.replace_audio(vocals_file)
    if output_video:
        print(f"✅ 已去除 BGM: {output_video}")


def example_5_extract_subtitles():
    """示例 5: 提取字幕"""
    print("=" * 60)
    print("示例 5: 提取字幕")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 方法 1: 从视频文件提取（如果有字幕轨道）
    subtitle_file = processor.extract_subtitles_ffmpeg()
    if subtitle_file:
        print(f"✅ 字幕已提取: {subtitle_file}")
    else:
        # 方法 2: 从在线视频提取（需要 yt-dlp）
        subtitle_file = processor.extract_subtitles_ytdlp(lang="zh-Hans")
        if subtitle_file:
            print(f"✅ 字幕已提取: {subtitle_file}")


def example_6_remove_audio():
    """示例 6: 去除视频中的音频"""
    print("=" * 60)
    print("示例 6: 去除音频（静音视频）")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    output_video = processor.remove_audio()
    if output_video:
        print(f"✅ 已去除音频: {output_video}")


def example_8_demucs_models():
    """示例 8: 使用不同的 Demucs 模型"""
    print("=" * 60)
    print("示例 8: 使用不同的 Demucs 模型")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    models = ["htdemucs", "htdemucs_ft", "mdx_extra"]

    for model in models:
        print(f"\n尝试模型: {model}")
        print("-" * 60)
        result = processor.extract_bgm_demucs_cli(model=model)

        if result:
            vocals_file, bgm_file = result
            print(f"✅ {model} 分离成功")
            print(f"   人声: {vocals_file}")
            print(f"   BGM: {bgm_file}")
        else:
            print(f"❌ {model} 分离失败")


def example_9_spleeter_fallback():
    """示例 9: 使用 Spleeter 作为备选方案"""
    print("=" * 60)
    print("示例 9: 使用 Spleeter 作为备选方案")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 先尝试 Demucs
    print("尝试使用 Demucs...")
    result = processor.extract_bgm_demucs_cli(model="htdemucs")

    if not result:
        print("Demucs 失败，尝试 Spleeter...")
        result = processor.extract_bgm_spleeter()

    if result:
        vocals_file, bgm_file = result
        print(f"✅ 分离成功")
        print(f"   人声: {vocals_file}")
        print(f"   BGM: {bgm_file}")
    else:
        print("❌ 所有方法都失败")
        print("   请安装 Demucs: pip install demucs")
        print("   或安装 Spleeter: pip install spleeter")


def example_7_complete_workflow():
    """示例 7: 完整工作流"""
    print("=" * 60)
    print("示例 7: 完整工作流")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 1. 提取音频
    print("\n1. 提取音频...")
    audio_file = processor.extract_audio()

    # 2. 分离人声和 BGM（使用 Demucs）
    print("\n2. 分离人声和 BGM（使用 Demucs）...")
    result = processor.extract_bgm_demucs_cli(model="htdemucs")

    if result:
        vocals_file, bgm_file = result

        # 3. 创建只有 BGM 的视频
        print("\n3. 创建只有 BGM 的视频...")
        video_bgm = processor.replace_audio(bgm_file)

        # 4. 创建只有人声的视频
        print("\n4. 创建只有人声的视频...")
        video_vocals = processor.replace_audio(vocals_file)

        # 5. 提取字幕
        print("\n5. 提取字幕...")
        subtitle_file = processor.extract_subtitles_ffmpeg()

        print("\n✅ 所有处理完成！")
        print(f"   音频: {audio_file}")
        print(f"   人声: {vocals_file}")
        print(f"   BGM: {bgm_file}")
        if video_bgm:
            print(f"   只有 BGM 的视频: {video_bgm}")
        if video_vocals:
            print(f"   只有人声的视频: {video_vocals}")
        if subtitle_file:
            print(f"   字幕: {subtitle_file}")
    else:
        print("\n❌ 音频分离失败")
        print("   请确保已安装 Demucs: pip install demucs")


def example_10_audio_separator():
    """示例 10: 使用 audio-separator（推荐，不依赖旧版 numpy）"""
    print("=" * 60)
    print("示例 10: 使用 audio-separator 分离人声和 BGM")
    print("=" * 60)

    processor = VideoAudioProcessor("downloads1/近年看过最好磕的武侠西皮！！！.mp4", output_dir="./output")

    # 使用 audio-separator（推荐方法）
    result = processor.extract_bgm_audio_separator(model="UVR-MDX-NET-Inst_HQ_3")

    if result:
        vocals_file, bgm_file = result
        print(f"✅ 人声文件: {vocals_file}")
        print(f"✅ BGM 文件: {bgm_file}")
    else:
        print("❌ 分离失败，请安装: pip install audio-separator")
        print("\n💡 audio-separator 的优点：")
        print("   - 不依赖旧版 numpy")
        print("   - 支持多种高质量模型")
        print("   - 安装简单，使用方便")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python video_audio_examples.py <example_number>")
        print("\n可用示例:")
        print("  1 - 提取音频")
        print("  2 - 分离人声和 BGM（Demucs）")
        print("  3 - 去除人声，保留 BGM")
        print("  4 - 去除 BGM，保留人声")
        print("  5 - 提取字幕")
        print("  6 - 去除音频")
        print("  7 - 完整工作流")
        print("  8 - 使用不同的 Demucs 模型")
        print("  9 - Spleeter 备选方案")
        sys.exit(1)

    example_num = sys.argv[1]

    examples = {
        '1': example_1_extract_audio,
        '2': example_2_separate_vocals_bgm,
        '3': example_3_remove_vocals,
        '4': example_4_remove_bgm,
        '5': example_5_extract_subtitles,
        '6': example_6_remove_audio,
        '7': example_7_complete_workflow,
        '8': example_8_demucs_models,
        '9': example_9_spleeter_fallback,
    }

    if example_num in examples:
        examples[example_num]()
    else:
        print(f"❌ 未知示例: {example_num}")

