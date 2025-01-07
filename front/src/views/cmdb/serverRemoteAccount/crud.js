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
      custom: [
        {
          thin: true,
          text: '关联服务器',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-share',
          show () {
            return vm.hasPermissions('serverAssociate')
          },
          emit: 'serverAssociate'
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
        title: '登录名称',
        key: 'remote_name',
        width: 145,
        disabled: false,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('remote_name')
        },
        form: {
          show: true,
          component: {
            span: 12
          }
        }
      },
      {
        title: '登录用户名',
        key: 'remote_username',
        width: 145,
        dict: {
          data: vm.dictionary('remote_username')
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
        title: '登录密码',
        key: 'remote_password',
        width: 145,
        type: 'input',
        form: {
          // show: true,
          component: {
            span: 12,
            showPassword: true,
            placeholder: '请输入密码'
          },
          editDisabled: false,
          itemProps: {
            class: { yxtInput: true }
          }
        },
        disabled: true
      },
      {
        title: '登录方式',
        key: 'remote_type',
        search: {
          disabled: true
        },
        width: 70,
        type: 'radio',
        dict: {
          data: vm.dictionary('remote_type_radio')
        },
        form: {
          value: true,
          component: {
            span: 12
          }
        }
      },
      {
        title: '密钥',
        key: 'remote_private_key',
        type: 'file-uploader',
        width: 60,
        align: 'left',
        form: {
          component: {
            props: {
              elProps: { // 与el-uploader 配置一致
                multiple: false,
                limit: 1 // 限制5个文件
              },
              sizeLimit: 500 * 1024 // 不能超过限制
            },
            span: 24
          },
          helper: '限制文件大小不能超过500k'
        }
      },
      {
        title: '备注说明',
        key: 'remark',
        width: 145,
        disabled: false,
        dict: {
          data: vm.dictionary('remark')
        },
        form: {
          show: true,
          component: {
            span: 12
          }
        }
      }
    ]
  }
}
