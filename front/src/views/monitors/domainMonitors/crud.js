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
      }
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
        title: '域名',
        key: 'domain_name',
        minWidth: 145,
        disabled: false,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('domain_name')
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
        key: 'domain_account',
        width: 145,
        dict: {
          data: vm.dictionary('domain_account')
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
        title: '到期天数',
        key: 'domain_expire_days',
        width: 100,
        dict: {
          data: vm.dictionary('domain_expire_days')
        },
        form: {
          show: false,
          component: {
            span: 12,
            disabled: true,
            show: false,
            style: {
              width: '100%',
              height: '100%',
              backgroundColor: '#f5f5f5',
              alignItems: 'center',
              color: 'rgba(0,0,0,0.65)'
            }
          }
        }
      },
      {
        title: '到期时间',
        key: 'domain_expire_time',
        width: 145,
        dict: {
          data: vm.dictionary('domain_expire_time')
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
        title: '证书状态',
        key: 'domain_status',
        width: 145,
        dict: {
          data: vm.dictionary('domain_status')
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
        title: '是否开启通知',
        key: 'domain_notice_enable',
        type: 'radio',
        width: 145,
        dict: {
          data: vm.dictionary('button_status_bool')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      }
    ]
  }
}
