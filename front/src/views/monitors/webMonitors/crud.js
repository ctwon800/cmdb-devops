// import { request } from '@/api/service'

// import color from "@/store/modules/d2admin/modules/color"

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      width: 320,
      fixed: 'right',
      view: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Retrieve')
        }
      },
      edit: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      },
      custom: [{
        text: '设为不监控',
        type: 'warning',
        size: 'small',
        emit: 'SetUnmonitor',
        disabled () {
          return !vm.hasPermissions('SetUnmonitor')
        }
      }]
    },
    viewOptions: {
      componentType: 'form'
    },
    formOptions: {
      defaultSpan: 12 // 默认的表单 span
    },
    indexRow: { // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 60
    },
    columns: [
      {
        title: 'web站点',
        key: 'web_uri',
        width: 180,
        disabled: false,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('web_uri')
        },
        form: {
          show: true,
          component: {
            span: 12
          }
        }
      },
      {
        title: '所属账号',
        key: 'web_account',
        width: 145,
        dict: {
          data: vm.dictionary('web_account')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'ID',
        key: 'id',
        disabled: true,
        form: {
          disabled: true
        }
      },
      {
        title: '网站状态',
        key: 'web_status',
        width: 80,
        dict: {
          data: vm.dictionary('web_status')
        },
        form: {
          show: false,
          component: {
            span: 12,
            disabled: true,
            show: false
          }
        }
      },
      {
        title: '是否启用通知',
        key: 'web_notice_enable',
        type: 'radio',
        width: 100,
        dict: {
          data: vm.dictionary('button_status_bool')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'HTTP检查是否启用',
        key: 'web_http_enable',
        type: 'radio',
        width: 100,
        dict: {
          data: vm.dictionary('button_status_bool')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'HTTPS检查是否启用',
        key: 'web_https_enable',
        type: 'radio',
        width: 100,
        dict: {
          data: vm.dictionary('button_status_bool')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '更新时间',
        key: 'update_time',
        width: 145,
        form: {
          show: false,
          component: {
            span: 12,
            disabled: true,
            show: false
          }
        }
      }
    ]
  }
}
