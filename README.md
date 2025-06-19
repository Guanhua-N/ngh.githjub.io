# 部署方法
## Windows
- 安装 [RubyInstaller](https://rubyinstaller.org/downloads/)。
  - 安装好后，运行 ruby -v 和 gem -v 确保版本正常。

- 在命令行中执行gem install bundler jekyll。

- 切换到academicpages项目目录下执行bundle install --verbose
    - --verbose是为了看命令执行的具体细节，观察哪里卡住了
    - 会卡住，因为需要访问国外网站下载以来
    - 更换 RubyGems 镜像源为清华，命令一定要在cmd中搞，不要用powershell
      - gem sources --remove https://rubygems.org/
      - gem sources --add https://mirrors.tuna.tsinghua.edu.cn/rubygems/
      - gem sources list验证安装是否成功
    - 修改项目根目录下的Gemfile
      - 将source "https://rubygems.org"改为source "https://mirrors.tuna.tsinghua.edu.cn/rubygems/"
      - 
- bundle exec jekyll serve后打开http://localhost:4000 就能预览

- bundle exec jekyll build会在根目录下生成_site文件夹，里面是纯静态网页文件（HTML/CSS/JS）。可以部署到ngix上。

## 一些细节
每次修改代码后想要预览直接bundle exec jekyll serve就行，不用bundle install

但是像生成新的静态页面文件必须要每次都bundle exec jekyll build