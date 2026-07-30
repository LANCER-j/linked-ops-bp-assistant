# 本地视觉素材

本仓库不包含《明日方舟》的干员头像、职业参考图或子职业图标字体。
软件缺少这些素材时会显示职业色占位卡和文字筛选，不影响 BP、拍卖、
存档及结算功能。

如需在本地补全干员头像与子职业图标字体，请在项目根目录运行：

```powershell
python tools/download_visual_assets.py data/operators.csv assets/avatars `
  --branch-font assets/ui/ak-class-icons-solid.ttf
```

脚本使用的上游来源：

- 干员头像：<https://github.com/yuanyan3060/ArknightsGameResource>
- 子职业图标：<https://github.com/tohmatosauce/ak-branch-icons>

下载内容不会被 Git 跟踪。素材版权及许可条件以对应上游仓库和权利人的
声明为准，本项目不对下载内容进行再分发。

`ui/linked_ops_logo.png`、不同尺寸的 PNG 及 `linked_ops_logo.ico` 是
联锁对抗项目自身使用的界面与 Windows 图标素材，会随源码仓库发布。
