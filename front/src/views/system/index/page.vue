
<template>
  <d2-container class="page">
    <div style="margin-bottom: 10px">
      <el-card class="box-card">
        <div>
          美好的一天，从使用 dvadmin2
          开始！您可以基于此系统进行持续开发，以做出符合自己系统。所有前端后台代码封装过后十分精简易上手，
          出错概率低。同时支持移动客户端访问。系统会陆续更新一些实用功能。
        </div>
      </el-card>
    </div>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <div slot="header" class="clearfix">
            <span>作者有话说</span>
            <a
              href="https://www.django-vue-admin.com/about/"
              style="float: right; padding: 3px 0; color: #409eff"
              target="_blank"
            >
              关于我们
            </a>
          </div>
          <div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <div>
          <el-card class="box-card">
            <div slot="header" class="clearfix">
              <span>友情链接</span>
              <a
                href="https://bbs.django-vue-admin.com/"
                style="float: right; padding: 3px 0; color: #409eff"
                target="_blank"
              >
                更多
              </a>
            </div>

            <el-row>
              <el-col
                :span="8"
                v-for="(li, index) in linkList"
                :key="index"
                class="yxt-linklist"
              >
                <h4>
                  <a :href="li.href" target="_blank" style="color: #409eff">
                    {{ li.name }}</a
                  >
                </h4>
                <div>
                  {{ li.content }}
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="10">
      <el-col :span="12">
        <div>这里放项目的更新情况,最新动态</div>
      </el-col>
    </el-row>
  </d2-container>
</template>

<script>
export default {
  data () {
    return {
      linkList: [
        {
          name: 'D2Admin',
          href: 'https://d2.pub/zh/doc/d2-admin/',
          content:
            'D2Admin是一个完全 开源免费 的企业中后台产品前端集成方案，使用最新的前端技术栈，助力管理系统快速开发。'
        },
        {
          name: 'd2-crud-plus',
          href: 'http://d2-crud-plus.docmirror.cn/d2-crud-plus/guide/',
          content:
            'd2-crud-plus 是基于 d2-admin 的 d2-crud 的扩展,旨在简化 d2-crud 配置，快速开发crud功能'
        },
        {
          name: 'D2Admin',
          content:
            'D2Admin是一个完全 开源免费 的企业中后台产品前端集成方案，使用最新的前端技术栈，助力管理系统快速开发。'
        },
        {
          name: 'D2Admin',
          content:
            'D2Admin是一个完全 开源免费 的企业中后台产品前端集成方案，使用最新的前端技术栈，助力管理系统快速开发。'
        },
        {
          name: 'D2Admin',
          content:
            'D2Admin是一个完全 开源免费 的企业中后台产品前端集成方案，使用最新的前端技术栈，助力管理系统快速开发。'
        },
        {
          name: 'D2Admin',
          content:
            'D2Admin是一个完全 开源免费 的企业中后台产品前端集成方案，使用最新的前端技术栈，助力管理系统快速开发。'
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  .btn-group {
    color: $color-text-placehoder;
    font-size: 12px;
    margin-top: 10px;
    margin-bottom: 10px;
    .btn-group__btn {
      color: $color-text-sub;
      &:hover {
        color: $color-text-main;
      }
      &.btn-group__btn--link {
        color: $color-primary;
      }
    }
  }
}
.yxt-linklist {
  border: 1px #f1f1f1 solid;
  padding: 5px 10px;
}
</style>
