// import { request } from '@/api/service'

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
        title: '集群名称',
        key: 'k8s_cluster_name',
        width: 100,
        disabled: false,
        search: {
          disabled: false
        },
        dict: {
          cache: true,
          data: vm.dictionary('k8s_cluster_name')
        },
        form: {
          show: false,
          component: {
            span: 12
          },
          rules: [ // 表单校验规则
            { required: true, message: '集群名称必填项' }
          ]
        }
      },
      {
        title: '集群描述',
        key: 'k8s_clustet_desc',
        width: 180,
        disabled: false,
        dict: {
          cache: true,
          data: vm.dictionary('k8s_cluster_name')
        },
        form: {
          disabled: false,
          rules: [ // 表单校验规则
            { required: true, message: '集群名称必填项' }
          ]
        }
      },
      {
        title: '默认命名空间',
        key: 'k8s_default_namespace',
        width: 145,
        disabled: false,
        search: {
          disabled: true
        },
        dict: {
          cache: true,
          data: vm.dictionary('k8s_default_namespace')
        },
        form: {
          disabled: false,
          component: {
            span: 12,
            placeholder: '只能一个,不填默认为default'
          }
        }
      },
      {
        title: '隐藏命名空间',
        key: 'k8s_exclude_namespace',
        width: 145,
        disabled: false,
        search: {
          disabled: true
        },
        dict: {
          cache: true,
          data: vm.dictionary('k8s_exclude_namespace')
        },
        form: {
          disabled: false,
          component: {
            span: 12,
            placeholder: '多个请用,隔开'
          }
        }
      },
      {
        title: '默认集群',
        key: 'k8s_cluster_is_default',
        width: 145,
        disabled: false,
        type: 'switch',
        search: {
          disabled: true
        },
        dict: {
          cache: true,
          data: vm.dictionary('k8s_cluster_is_default')
        },
        form: {
          disabled: false,
          component: {
            placeholder: '请选择是否'
          },
          valueChange (key, value) {
            console.log('-----你选择了', value)
          }
        }
      },
      {
        title: '集群连接配置',
        key: 'k8s_cluster_config',
        width: 145,
        disabled: true,
        dict: {
          data: vm.dictionary('k8s_cluster_config')
        },
        form: {
          show: false,
          component: {
            // span: 64,
            placeholder: '请将config内容base64加密后填入'
          },
          rules: [ // 表单校验规则
            { required: true, message: '集群连接配置必填项' }
          ]
        }
      }
    ]
  }
}
