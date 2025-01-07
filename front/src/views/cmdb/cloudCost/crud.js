// import { request } from '@/api/service'

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      // tableType: 'vxe-table',
      // rowKey: true,
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      width: 240,
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
        title: '平台',
        key: 'server_platform',
        width: 100,
        disabled: false,
        search: {
          disabled: false
        },
        type: 'select',
        dict: {
          cache: true,
          url: '/api/cmdb/server_platform/',
          value: 'id',
          label: 'server_platform'
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '账号',
        key: 'account_name',
        width: 145,
        disabled: false,
        search: {
          disabled: false
        },
        type: 'select',
        dict: {
          cache: true,
          url: '/api/cmdb/account_management/',
          value: 'id',
          label: 'account_name'
        },
        form: {
          show: true,
          component: {
            span: 12,
            props: {
              clearable: true,
              elProps: {
                allowCreate: true,
                filterable: true,
                clearable: true
              }
            }
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
        title: '账单月份',
        key: 'bill_cycle',
        width: 145,
        disabled: false,
        search: {
          disabled: false
        },
        type: 'select',
        dict: {
          cache: true,
          url: '/api/cmdb/cloud_cost/get_month_list/',
          value: 'bill_cycle',
          label: 'bill_cycle'
        },
        form: {
          show: true,
          component: {
            span: 12,
            props: {
              clearable: true,
              elProps: {
                allowCreate: true,
                filterable: true,
                clearable: true
              }
            }
          }
        }
      },
      {
        title: '费用',
        key: 'cost',
        width: 145,
        dict: {
          data: vm.dictionary('cost')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '费用-美元',
        key: 'cost_usd',
        width: 145,
        dict: {
          data: vm.dictionary('cost_usd')
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
