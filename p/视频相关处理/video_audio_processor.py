#!/usr/bin/env python3
"""
视频音频处理工具
功能：
1. 提取视频的 BGM
2. 提取视频的人声
3. 去除视频的人声
4. 去除视频的 BGM
5. 字幕提取
"""

import subprocess
import os
import argparse
import json
from pathlib import Path
from typing import Optional, List, Tuple


class VideoAudioProcessor:
    def __init__(self, video_file: str, output_dir: str = "./output"):
        self.video_file = video_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        if not os.path.exists(video_file):
            raise FileNotFoundError(f"视频文件不存在: {video_file}")

    def _run_ffmpeg(self, cmd: List[str], description: str = "") -> bool:
        """运行 FFmpeg 命令"""
        try:
            if description:
                print(f"正在{description}...")

            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            if description:
                print(f"✅ {description}完成")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 错误: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ 错误: 未找到 FFmpeg，请先安装 FFmpeg")
            return False

    def extract_audio(self, output_file: Optional[str] = None,
                      format: str = "mp3", quality: str = "192k") -> Optional[str]:
        """
        提取视频中的音频

        参数:
            output_file: 输出文件路径
            format: 音频格式 (mp3, m4a, wav, flac)
            quality: 音质 (128k, 192k, 256k, 320k)

        返回:
            输出文件路径
        """
        if output_file is None:
            video_name = Path(self.video_file).stem
            output_file = os.path.join(self.output_dir, f"{video_name}_audio.{format}")

        cmd = ['ffmpeg', '-i', self.video_file, '-vn']  # 不包含视频

        # 根据格式设置编码器
        if format == 'mp3':
            cmd.extend(['-acodec', 'libmp3lame', '-ab', quality])
        elif format == 'wav':
            cmd.extend(['-acodec', 'pcm_s16le'])  # WAV 使用 PCM 编码
        elif format == 'flac':
            cmd.extend(['-acodec', 'flac'])
        else:
            cmd.extend(['-acodec', 'copy'])  # 其他格式直接复制

        cmd.extend(['-y', output_file])  # 覆盖输出文件

        if self._run_ffmpeg(cmd, f"提取音频为 {format}"):
            return output_file
        return None

    def extract_bgm_demucs(self, output_dir: Optional[str] = None,
                           model: str = "htdemucs") -> Optional[Tuple[str, str]]:
        """
        使用 Demucs API 分离 BGM 和人声（推荐，效果更好）

        需要安装: pip install demucs torchaudio

        参数:
            output_dir: 输出目录
            model: 模型名称 (htdemucs, htdemucs_ft, mdx_extra, etc.)

        返回:
            (人声文件路径, BGM文件路径)
        """
        try:
            import torch
            import torchaudio
            from demucs import pretrained
            from demucs.apply import apply_model
            from demucs.audio import convert_audio
        except ImportError:
            print("❌ 需要安装 Demucs: pip install demucs torchaudio")
            return None

        # 先提取音频
        audio_file = self.extract_audio(format="wav")
        if not audio_file:
            return None

        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "demucs_output")

        os.makedirs(output_dir, exist_ok=True)

        print(f"正在使用 Demucs ({model}) 分离音频...")
        print("（这可能需要几分钟，请耐心等待）")

        try:
            # 加载模型
            model_obj = pretrained.get_model(model)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_obj.to(device)

            # 处理 BagOfModels 对象（某些模型返回的是模型集合）
            # 获取实际的模型对象和采样率
            if hasattr(model_obj, 'models') and len(model_obj.models) > 0:
                # 如果是 BagOfModels，使用第一个模型的属性
                actual_model = model_obj.models[0]
                sample_rate = actual_model.sample_rate
                channels = actual_model.channels
            else:
                # 单个模型对象
                sample_rate = model_obj.sample_rate
                channels = model_obj.channels

            # 加载音频
            wav, sr = torchaudio.load(audio_file)
            wav = convert_audio(wav, sr, sample_rate, channels)
            wav = wav.to(device)

            # 分离
            with torch.no_grad():
                sources = apply_model(model_obj, wav[None])[0]

            # Demucs 输出：vocals, drums, bass, other
            vocals = sources[3].cpu()  # vocals 是第4个（索引3）
            # BGM = drums + bass + other
            bgm = sources[0] + sources[1] + sources[2]  # drums, bass, other
            bgm = bgm.cpu()

            # 保存文件
            audio_name = Path(audio_file).stem
            vocals_file = os.path.join(output_dir, f"{audio_name}_vocals.wav")
            bgm_file = os.path.join(output_dir, f"{audio_name}_bgm.wav")

            torchaudio.save(vocals_file, vocals, sample_rate)
            torchaudio.save(bgm_file, bgm, sample_rate)

            if os.path.exists(vocals_file) and os.path.exists(bgm_file):
                print("✅ 音频分离完成")
                return (vocals_file, bgm_file)
            else:
                print("❌ 分离失败：未找到输出文件")
                return None

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Demucs API 分离失败: {error_msg}")
            if "torchcodec" in error_msg.lower():
                print("   检测到需要 torchcodec，自动切换到命令行方式...")
            else:
                print("   尝试使用命令行方式...")
            return self.extract_bgm_demucs_cli(output_dir, model)

    def extract_bgm_demucs_cli(self, output_dir: Optional[str] = None,
                               model: str = "htdemucs") -> Optional[Tuple[str, str]]:
        """
        使用 Demucs 命令行工具分离 BGM 和人声（更简单的方法）

        需要安装: pip install demucs

        返回:
            (人声文件路径, BGM文件路径)
        """
        # 先提取音频
        audio_file = self.extract_audio(format="wav")
        if not audio_file:
            return None

        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "demucs_output")

        print(f"正在使用 Demucs ({model}) 分离音频...")
        print("（这可能需要几分钟，请耐心等待）")

        try:
            # 使用 Demucs 命令行工具
            # 注意：音频文件必须作为位置参数放在最后
            # 使用 --flac 或 --mp3 可以避免 torchcodec 的问题
            cmd = [
                'python3', '-m', 'demucs.separate',
                '--two-stems', 'vocals',  # 只分离人声和伴奏（注意：不是 --two-stems=vocals）
                '-n', model,
                '--out', output_dir,
                audio_file  # 音频文件作为位置参数
            ]

            # 调试：打印实际执行的命令
            print(f"执行命令: {' '.join(cmd)}")
            
            # 设置环境变量，强制使用 soundfile 后端而不是 torchcodec
            env = os.environ.copy()
            env['TORCHAUDIO_USE_SOUNDFILE'] = '1'
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)

            # Demucs 输出目录结构可能是：
            # - output_dir/separated/model/audio_name/vocals.wav (默认，WAV格式)
            # - output_dir/separated/model/audio_name/vocals.flac (使用 --flac 时)
            # - output_dir/model/audio_name/vocals.wav (如果指定了 --out)
            audio_name = Path(audio_file).stem
            
            # 尝试多个可能的路径和格式
            possible_dirs = [
                os.path.join(output_dir, "separated", model, audio_name),  # 默认结构
                os.path.join(output_dir, model, audio_name),  # 直接输出结构
            ]
            
            # 可能的文件扩展名（WAV 或 FLAC）
            possible_extensions = ['.flac', '.wav']
            
            vocals_file = None
            no_vocals_file = None
            
            for separated_dir in possible_dirs:
                for ext in possible_extensions:
                    test_vocals = os.path.join(separated_dir, f"vocals{ext}")
                    test_no_vocals = os.path.join(separated_dir, f"no_vocals{ext}")
                    if os.path.exists(test_vocals) and os.path.exists(test_no_vocals):
                        vocals_file = test_vocals
                        no_vocals_file = test_no_vocals
                        break
                if vocals_file:
                    break

            if vocals_file and no_vocals_file:
                print("✅ 音频分离完成")
                return (vocals_file, no_vocals_file)
            else:
                print("❌ 分离失败：未找到输出文件")
                print(f"   已检查的目录: {possible_dirs}")
                return None

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or str(e)
            print(f"❌ Demucs 分离失败: {error_msg}")
            print("\n💡 建议解决方案：")
            print("   1. 安装 soundfile: pip install soundfile")
            print("   2. 或者尝试重新安装 torchcodec: pip install --force-reinstall torchcodec")
            return None
        except FileNotFoundError as e:
            print(f"❌ Demucs 分离失败: {e.strerror}")
            print("❌ 未找到 Demucs，请安装: pip install demucs")
            return None

    def extract_bgm_audio_separator(self, output_dir: Optional[str] = None,
                                    model: str = "UVR-MDX-NET-Inst_HQ_3") -> Optional[Tuple[str, str]]:
        """
        使用 audio-separator 分离 BGM 和人声（推荐替代方案）

        需要安装: pip install audio-separator

        参数:
            output_dir: 输出目录
            model: 模型名称，可选值：
                   - UVR-MDX-NET-Inst_HQ_3 (默认，高质量)
                   - Kim_Vocal_2
                   - UVR-MDX-NET-1_HP
                   - 等等

        返回:
            (人声文件路径, BGM文件路径)
        """
        try:
            from audio_separator import Separator
        except ImportError:
            print("❌ 需要安装 audio-separator: pip install audio-separator")
            print("   这是一个现代的音频分离库，不依赖旧版 numpy")
            return None

        # 先提取音频
        audio_file = self.extract_audio(format="wav")
        if not audio_file:
            return None

        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "audio_separator_output")

        os.makedirs(output_dir, exist_ok=True)

        print(f"正在使用 audio-separator (模型: {model}) 分离音频...")
        print("（这可能需要几分钟，请耐心等待）")

        try:
            separator = Separator(model_name=model, output_dir=output_dir)
            output_files = separator.separate(audio_file)

            # audio-separator 返回分离后的文件列表
            # 通常第一个是人声，第二个是伴奏
            if len(output_files) >= 2:
                vocals_file = output_files[0] if 'vocals' in output_files[0].lower() else output_files[0]
                bgm_file = output_files[1] if 'instrumental' in output_files[1].lower() or 'accompaniment' in output_files[1].lower() else output_files[1]
                
                if os.path.exists(vocals_file) and os.path.exists(bgm_file):
                    print("✅ 音频分离完成")
                    return (vocals_file, bgm_file)
            else:
                # 如果返回格式不同，尝试查找文件
                audio_name = Path(audio_file).stem
                possible_vocals = [
                    os.path.join(output_dir, f"{audio_name}_vocals.wav"),
                    os.path.join(output_dir, f"{audio_name}_vocal.wav"),
                    os.path.join(output_dir, "vocals.wav"),
                ]
                possible_bgm = [
                    os.path.join(output_dir, f"{audio_name}_instrumental.wav"),
                    os.path.join(output_dir, f"{audio_name}_accompaniment.wav"),
                    os.path.join(output_dir, f"{audio_name}_no_vocals.wav"),
                    os.path.join(output_dir, "instrumental.wav"),
                ]
                
                vocals_file = next((f for f in possible_vocals if os.path.exists(f)), None)
                bgm_file = next((f for f in possible_bgm if os.path.exists(f)), None)
                
                if vocals_file and bgm_file:
                    print("✅ 音频分离完成")
                    return (vocals_file, bgm_file)

            print("❌ 分离失败：未找到输出文件")
            return None

        except Exception as e:
            print(f"❌ audio-separator 分离失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def extract_bgm_spleeter(self, output_dir: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        使用 Spleeter 分离 BGM 和人声

        需要安装: pip install spleeter

        返回:
            (人声文件路径, BGM文件路径)
        """
        print("ℹ️  使用 Spleeter 分离音频（如果遇到问题，建议使用 audio-separator）")

        try:
            from spleeter.separator import Separator
        except ImportError:
            print("❌ 需要安装 Spleeter: pip install spleeter")
            print("   或者使用 Demucs: pip install demucs")
            return None

        # 先提取音频
        audio_file = self.extract_audio(format="wav")
        if not audio_file:
            return None

        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "spleeter_output")

        os.makedirs(output_dir, exist_ok=True)

        print("正在使用 Spleeter 分离音频...")
        print("（这可能需要几分钟，请耐心等待）")

        try:
            # 使用 2stems 模型（人声和伴奏）
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(audio_file, output_dir)

            # Spleeter 输出目录结构
            audio_name = Path(audio_file).stem
            vocals_file = os.path.join(output_dir, audio_name, "vocals.wav")
            accompaniment_file = os.path.join(output_dir, audio_name, "accompaniment.wav")

            if os.path.exists(vocals_file) and os.path.exists(accompaniment_file):
                print("✅ 音频分离完成")
                return (vocals_file, accompaniment_file)
            else:
                print("❌ 分离失败：未找到输出文件")
                return None

        except Exception as e:
            print(f"❌ Spleeter 分离失败: {e}")
            return None

    def extract_bgm_ffmpeg_center(self, output_dir: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        使用 FFmpeg 简单方法分离人声和 BGM（效果一般，作为备选方案）
        
        原理：提取中心声道（通常是人声）和侧声道（通常是伴奏）
        注意：这种方法效果有限，仅适用于立体声音频，且人声在中心的情况

        返回:
            (人声文件路径, BGM文件路径)
        """
        # 先提取音频
        audio_file = self.extract_audio(format="wav")
        if not audio_file:
            return None

        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "ffmpeg_output")

        os.makedirs(output_dir, exist_ok=True)

        audio_name = Path(audio_file).stem
        vocals_file = os.path.join(output_dir, f"{audio_name}_vocals.wav")
        bgm_file = os.path.join(output_dir, f"{audio_name}_bgm.wav")

        print("正在使用 FFmpeg 简单方法分离音频...")
        print("⚠️  注意：此方法效果有限，仅适用于立体声音频")

        try:
            # 提取中心声道（人声）
            cmd_vocals = [
                'ffmpeg',
                '-i', audio_file,
                '-af', 'pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1',  # 提取中心
                '-y',
                vocals_file
            ]

            # 提取侧声道（伴奏）
            cmd_bgm = [
                'ffmpeg',
                '-i', audio_file,
                '-af', 'pan=stereo|c0=0.5*c0+-0.5*c1|c1=-0.5*c0+0.5*c1',  # 提取侧声道
                '-y',
                bgm_file
            ]

            if self._run_ffmpeg(cmd_vocals, "提取人声") and self._run_ffmpeg(cmd_bgm, "提取伴奏"):
                if os.path.exists(vocals_file) and os.path.exists(bgm_file):
                    print("✅ 音频分离完成（FFmpeg 方法）")
                    return (vocals_file, bgm_file)

            print("❌ FFmpeg 分离失败")
            return None

        except Exception as e:
            print(f"❌ FFmpeg 分离失败: {e}")
            return None

    def extract_bgm_ffmpeg(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        使用 FFmpeg 提取 BGM（简单方法：提取所有音频）
        注意：这只是提取音频，无法真正分离 BGM 和人声
        """
        if output_file is None:
            video_name = Path(self.video_file).stem
            output_file = os.path.join(self.output_dir, f"{video_name}_bgm.mp3")

        # 这只是提取音频，不是真正的 BGM 分离
        return self.extract_audio(output_file, format="mp3")

    def remove_audio(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        去除视频中的音频（静音视频）

        返回:
            输出文件路径
        """
        if output_file is None:
            video_name = Path(self.video_file).stem
            output_file = os.path.join(self.output_dir, f"{video_name}_no_audio.mp4")

        cmd = [
            'ffmpeg',
            '-i', self.video_file,
            '-c', 'copy',  # 复制视频流，不重新编码
            '-an',  # 不包含音频
            '-y',
            output_file
        ]

        if self._run_ffmpeg(cmd, "去除音频"):
            return output_file
        return None

    def replace_audio(self, audio_file: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        替换视频中的音频

        参数:
            audio_file: 新的音频文件
            output_file: 输出文件路径
        """
        if output_file is None:
            video_name = Path(self.video_file).stem
            output_file = os.path.join(self.output_dir, f"{video_name}_new_audio.mp4")

        cmd = [
            'ffmpeg',
            '-i', self.video_file,
            '-i', audio_file,
            '-c:v', 'copy',  # 复制视频流
            '-c:a', 'aac',  # 音频编码为 AAC
            '-map', '0:v:0',  # 使用第一个输入的视频
            '-map', '1:a:0',  # 使用第二个输入的音频
            '-shortest',  # 以较短的流为准
            '-y',
            output_file
        ]

        if self._run_ffmpeg(cmd, "替换音频"):
            return output_file
        return None

    def extract_subtitles_ffmpeg(self, output_file: Optional[str] = None) -> Optional[str]:
        """
        使用 FFmpeg 提取字幕（如果视频包含字幕轨道）

        返回:
            字幕文件路径
        """
        # 先检查是否有字幕轨道
        cmd_check = [
            'ffprobe',
            '-v', 'quiet',
            '-select_streams', 's',
            '-show_entries', 'stream=index,codec_name',
            '-of', 'json',
            self.video_file
        ]

        try:
            result = subprocess.run(cmd_check, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            if not data.get('streams'):
                print("⚠️  视频中没有字幕轨道")
                return None

            print(f"找到 {len(data['streams'])} 个字幕轨道")

        except Exception as e:
            print(f"⚠️  检查字幕轨道失败: {e}")
            return None

        if output_file is None:
            video_name = Path(self.video_file).stem
            output_file = os.path.join(self.output_dir, f"{video_name}_subtitles.srt")

        cmd = [
            'ffmpeg',
            '-i', self.video_file,
            '-map', '0:s:0',  # 提取第一个字幕轨道
            '-y',
            output_file
        ]

        if self._run_ffmpeg(cmd, "提取字幕"):
            return output_file
        return None

    def extract_subtitles_ytdlp(self, output_file: Optional[str] = None,
                                lang: str = "zh-Hans") -> Optional[str]:
        """
        使用 yt-dlp 提取字幕（适用于在线视频）

        需要安装: pip install yt-dlp

        参数:
            output_file: 输出文件路径
            lang: 字幕语言
        """
        try:
            import yt_dlp
        except ImportError:
            print("❌ 需要安装 yt-dlp: pip install yt-dlp")
            return None

        if output_file is None:
            video_name = Path(self.video_file).stem
            output_file = os.path.join(self.output_dir, f"{video_name}_subtitles.srt")

        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'skip_download': True,  # 只下载字幕，不下载视频
            'outtmpl': output_file.replace('.srt', ''),
        }

        try:
            print(f"正在提取字幕（语言: {lang}）...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_file])

            # yt-dlp 会自动添加语言后缀
            lang_file = output_file.replace('.srt', f'.{lang}.srt')
            if os.path.exists(lang_file):
                # 重命名为标准名称
                os.rename(lang_file, output_file)
                print(f"✅ 字幕已提取: {output_file}")
                return output_file
            else:
                print("⚠️  未找到字幕文件")
                return None

        except Exception as e:
            print(f"❌ 提取字幕失败: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description='视频音频处理工具')
    parser.add_argument('video_file', help='视频文件路径或 URL')
    parser.add_argument('--output-dir', default='./output', help='输出目录')

    # 功能选择
    parser.add_argument('--extract-audio', action='store_true', help='提取音频')
    parser.add_argument('--extract-bgm', action='store_true', help='提取 BGM')
    parser.add_argument('--extract-vocals', action='store_true', help='提取人声')
    parser.add_argument('--remove-audio', action='store_true', help='去除音频')
    parser.add_argument('--remove-vocals', action='store_true', help='去除人声（保留 BGM）')
    parser.add_argument('--remove-bgm', action='store_true', help='去除 BGM（保留人声）')
    parser.add_argument('--extract-subtitles', action='store_true', help='提取字幕')

    # 参数
    parser.add_argument('--audio-format', default='mp3', choices=['mp3', 'm4a', 'wav', 'flac'],
                        help='音频格式')
    parser.add_argument('--audio-quality', default='192k', help='音频质量')
    parser.add_argument('--subtitle-lang', default='zh-Hans', help='字幕语言')

    # 音频分离方法
    parser.add_argument('--method', 
                        choices=['demucs', 'spleeter', 'audio-separator', 'ffmpeg-center'],
                        default='audio-separator',
                        help='音频分离方法（默认: audio-separator，推荐，不依赖旧版 numpy）')
    parser.add_argument('--demucs-model', default='htdemucs',
                        choices=['htdemucs', 'htdemucs_ft', 'mdx_extra', 'mdx_extra_q'],
                        help='Demucs 模型（默认: htdemucs）')
    parser.add_argument('--audio-separator-model', default='UVR-MDX-NET-Inst_HQ_3',
                        help='audio-separator 模型（默认: UVR-MDX-NET-Inst_HQ_3）')

    args = parser.parse_args()

    print("=" * 60)
    print("视频音频处理工具")
    print("=" * 60)

    try:
        processor = VideoAudioProcessor(args.video_file, args.output_dir)

        results = {}

        # 1. 提取音频
        if args.extract_audio:
            output = processor.extract_audio(format=args.audio_format, quality=args.audio_quality)
            if output:
                results['audio'] = output

        # 辅助函数：根据方法选择分离函数
        def separate_audio():
            """根据选择的方法分离音频"""
            if args.method == 'demucs':
                return processor.extract_bgm_demucs_cli(model=args.demucs_model)
            elif args.method == 'spleeter':
                return processor.extract_bgm_spleeter()
            elif args.method == 'audio-separator':
                return processor.extract_bgm_audio_separator(model=args.audio_separator_model)
            elif args.method == 'ffmpeg-center':
                return processor.extract_bgm_ffmpeg_center()
            else:
                return None

        # 2. 提取 BGM
        if args.extract_bgm:
            result = separate_audio()
            if result:
                vocals, bgm = result
                results['vocals'] = vocals
                results['bgm'] = bgm
            else:
                # 降级：只提取音频
                output = processor.extract_bgm_ffmpeg()
                if output:
                    results['bgm'] = output
                    print("⚠️  注意：这只是提取了音频，不是真正的 BGM 分离")
                    print(f"   如需真正分离 BGM，请使用 --method {args.method}")

        # 3. 提取人声
        if args.extract_vocals:
            result = separate_audio()
            if result:
                vocals, bgm = result
                results['vocals'] = vocals
                results['bgm'] = bgm
            else:
                print(f"❌ 提取人声失败，请检查是否安装了 {args.method}")

        # 4. 去除音频
        if args.remove_audio:
            output = processor.remove_audio()
            if output:
                results['no_audio'] = output

        # 5. 去除人声（保留 BGM）
        if args.remove_vocals:
            result = separate_audio()
            if result:
                vocals, bgm = result
                # 用 BGM 替换原视频的音频
                output = processor.replace_audio(bgm)
                if output:
                    results['no_vocals'] = output
            else:
                print(f"❌ 去除人声失败，请检查是否安装了 {args.method}")

        # 6. 去除 BGM（保留人声）
        if args.remove_bgm:
            result = separate_audio()
            if result:
                vocals, bgm = result
                # 用人声替换原视频的音频
                output = processor.replace_audio(vocals)
                if output:
                    results['no_bgm'] = output
            else:
                print(f"❌ 去除 BGM 失败，请检查是否安装了 {args.method}")

        # 7. 提取字幕
        if args.extract_subtitles:
            # 先尝试 FFmpeg（本地视频）
            output = processor.extract_subtitles_ffmpeg()
            if not output:
                # 再尝试 yt-dlp（在线视频）
                output = processor.extract_subtitles_ytdlp(lang=args.subtitle_lang)
            if output:
                results['subtitles'] = output

        # 输出结果
        if results:
            print("\n" + "=" * 60)
            print("处理完成！")
            print("=" * 60)
            for key, path in results.items():
                print(f"{key}: {path}")
        else:
            print("\n⚠️  未执行任何操作，请指定要执行的功能")
            print("\n示例:")
            print("  python video_audio_processor.py video.mp4 --extract-audio")
            print("  python video_audio_processor.py video.mp4 --extract-bgm --use-spleeter")
            print("  python video_audio_processor.py video.mp4 --extract-subtitles")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

