# 项目 Git 审核与回滚约定

本项目采用“稳定基线 + 独立更新分支 + 小步提交 + GitHub 审核”的方式管理更新。

## Codex 后续修改必须遵守

1. 不直接在 `main` 上开发。
2. 每项更新从当前稳定版本建立 `codex/<任务名称>-<日期>` 分支。
3. 开始修改前建立 `baseline/...` 标签，标记更新前状态。
4. 每个可独立理解、可独立撤销的改动单独提交，提交信息说明实际效果。
5. 提交时只明确加入本次相关文件，不使用“提交全部文件”。
6. 不提交 EXE、发布目录、干员头像、游戏字体、比赛存档、测试报告及其他游戏素材。
7. 推送后通过 GitHub Pull Request 的“Files changed”页面审核差异。
8. 不强制推送，不改写已经推送的历史。

## 审核修改

查看尚未提交的修改：

```powershell
git status
git diff
```

查看某次提交修改了什么：

```powershell
git show <提交编号>
```

查看最近的版本记录：

```powershell
git log --oneline --decorate -20
```

## 撤销方法

撤销尚未提交的单个文件：

```powershell
git restore -- <文件路径>
```

撤销已经提交并推送的某次更新：

```powershell
git revert <提交编号>
git push
```

`git revert` 会生成一条新的“撤销提交”，原始修改和撤销过程都会保留，适合审核。不要使用 `git reset --hard` 或强制推送处理已经公开的提交。

恢复到本轮更新开始前，可从对应的 `baseline/...` 标签创建检查分支：

```powershell
git switch -c review/baseline <基线标签>
```

## 发布约定

Python 源码、测试、素材提取工具可以进入仓库。EXE、发布文件夹和通过工具提取的游戏素材只保留在本地，不上传公开仓库。
