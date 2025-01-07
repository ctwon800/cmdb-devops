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
      width: 300,
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
      custom: [
        {
          thin: true,
          text: '更新云资源',
          size: 'small',
          type: 'warning',
          icon: 'el-icon-refresh-left',
          show () {
            return vm.hasPermissions('UpdateYunresource')
          },
          emit: 'updateYunresource'
        }
      ]
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
          disabled: false,
          component: {
            props: {
              clearable: true
            }
          }
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
        title: '账号名',
        key: 'account_name',
        minWidth: 145,
        disabled: false,
        search: {
          disabled: false
        },
        type: 'input',
        form: {
          show: true,
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
        title: '云账号用户名',
        key: 'login_username',
        minWidth: 145,
        type: 'input',
        form: {
          show: false,
          component: {
            span: 12,
            placeholder: '请输入云账号用户名'
          }
        },
        itemProps: {
          class: { yxtInput: true }
        }
      },
      {
        title: 'accesskey_id',
        key: 'accesskey_id',
        minWidth: 145,
        type: 'input',
        form: {
          show: false,
          component: {
            span: 12,
            placeholder: '请输入访问id'
          }
        },
        itemProps: {
          class: { yxtInput: true }
        }
      },
      {
        title: 'accesskey_secret',
        key: 'accesskey_secret',
        width: 145,
        type: 'input',
        form: {
          // show: true,
          component: {
            span: 12,
            showPassword: true,
            placeholder: '请输入访问密钥'
          },
          editDisabled: false,
          itemProps: {
            class: { yxtInput: true }
          }
        },
        disabled: true
      },
      {
        title: '区域',
        key: 'region',
        width: 145,
        type: 'input',
        form: {
          show: false,
          component: {
            span: 12,
            placeholder: '多个区域用逗号分割'
          }
        },
        itemProps: {
          class: { yxtInput: true }
        }
      }
    ]
  }
}
